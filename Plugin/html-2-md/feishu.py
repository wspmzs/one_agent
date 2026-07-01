# -*- coding: utf-8 -*-
"""飞书文档API集成 — 结构化提取wiki/docx/doc内容。"""

import asyncio
import base64
import re
import time
from typing import Optional
from urllib.parse import urlparse

import httpx

import utils


# ============================================================================
# 飞书 API 端点
# ============================================================================

FEISHU_AUTH_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
FEISHU_BLOCKS_URL = "https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks"
FEISHU_META_URL = "https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}"
FEISHU_WIKI_NODE_URL = "https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node"
FEISHU_IMAGE_URL = "https://open.feishu.cn/open-apis/drive/v1/medias/{token}/download"

# Token 缓存（2小时过期）
_token_cache: dict = {}

# 飞书块类型常量
BLOCK_PAGE = 1
BLOCK_TEXT = 2
BLOCK_H1 = 3
BLOCK_H2 = 4
BLOCK_H3 = 5
BLOCK_H4 = 6
BLOCK_H5 = 7
BLOCK_H6 = 8
BLOCK_H7 = 9
BLOCK_H8 = 10
BLOCK_H9 = 11
BLOCK_BULLET = 12
BLOCK_ORDERED = 13
BLOCK_CODE = 14
BLOCK_QUOTE = 15
BLOCK_TODO = 17
BLOCK_CALLOUT = 19
BLOCK_DIVIDER = 22
BLOCK_IMAGE = 27
BLOCK_TABLE = 31
BLOCK_TABLE_CELL = 32
BLOCK_QUOTE_CONTAINER = 34

HEADING_TYPES = {BLOCK_H1: "#", BLOCK_H2: "##", BLOCK_H3: "###",
                 BLOCK_H4: "####", BLOCK_H5: "#####",
                 BLOCK_H6: "######", BLOCK_H7: "######",
                 BLOCK_H8: "######", BLOCK_H9: "######"}

# ============================================================================
# URL 检测与解析
# ============================================================================

def is_feishu_url(url: str) -> bool:
    """判断是否飞书文档URL。"""
    try:
        p = urlparse(url)
        return (p.hostname and (
            p.hostname.endswith(".feishu.cn") or
            p.hostname.endswith(".larksuite.com")
        )) and bool(re.match(r'^/(wiki|docx|docs?)/[\w-]+', p.path))
    except Exception:
        return False

def parse_feishu_url(url: str) -> dict:
    """解析飞书URL：提取文档类型和token。

    Returns:
        {"type": "wiki"|"docx"|"doc", "token": "xxx"}
    """
    p = urlparse(url)
    m = re.match(r'^/(wiki|docx|docs?)/([\w-]+)', p.path)
    if not m:
        return {"type": None, "token": None}
    raw = m.group(1)
    return {"type": "doc" if raw == "docs" else raw, "token": m.group(2)}

# ============================================================================
# 认证 — Tenant Access Token
# ============================================================================

async def _get_tenant_token(app_id: str, app_secret: str) -> str:
    """获取 tenant_access_token（2小时缓存）。"""
    cache_key = f"{app_id}:{app_secret[:8]}"
    cached = _token_cache.get(cache_key)
    if cached and time.time() < cached["expires"]:
        return cached["token"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(FEISHU_AUTH_URL, json={
            "app_id": app_id,
            "app_secret": app_secret,
        }, headers={"Content-Type": "application/json; charset=utf-8"})
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"飞书认证失败: {data.get('msg', 'unknown')} (code={data.get('code')})")

        token = data["tenant_access_token"]
        _token_cache[cache_key] = {
            "token": token,
            "expires": time.time() + data.get("expire", 7200) - 300,  # 提前5分钟刷新
        }
        return token

# ============================================================================
# 文档ID解析
# ============================================================================

async def _resolve_document_id(
    token: str,
    doc_type: str,
    app_id: str,
    app_secret: str,
) -> Optional[dict]:
    """wiki需通过get_node API解析为document_id。"""
    if doc_type == "wiki":
        access_token = await _get_tenant_token(app_id, app_secret)
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                FEISHU_WIKI_NODE_URL,
                params={"token": token},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            data = resp.json()
            if data.get("code") != 0:
                raise RuntimeError(f"Wiki节点解析失败: {data.get('msg')}")
            node = data["data"]["node"]
            return {"document_id": node["obj_token"], "obj_type": node.get("obj_type", "docx")}
    return {"document_id": token, "obj_type": "doc" if doc_type == "doc" else "docx"}

# ============================================================================
# 文档块获取
# ============================================================================

async def _fetch_all_blocks(
    doc_id: str,
    app_id: str,
    app_secret: str,
) -> list:
    """分页获取文档所有块。"""
    access_token = await _get_tenant_token(app_id, app_secret)
    all_blocks = []
    page_token = None

    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            params = {"page_size": 500, "document_revision_id": "-1"}
            if page_token:
                params["page_token"] = page_token

            resp = await client.get(
                FEISHU_BLOCKS_URL.format(doc_id=doc_id),
                params=params,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            data = resp.json()
            if data.get("code") != 0:
                raise RuntimeError(f"获取文档块失败: {data.get('msg')}")

            items = data.get("data", {}).get("items", [])
            all_blocks.extend(items)

            if not data.get("data", {}).get("has_more"):
                break
            page_token = data["data"]["page_token"]

    return all_blocks

async def _fetch_doc_meta(
    doc_id: str,
    app_id: str,
    app_secret: str,
) -> Optional[dict]:
    """获取文档元数据（标题、作者）。"""
    try:
        access_token = await _get_tenant_token(app_id, app_secret)
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                FEISHU_META_URL.format(doc_id=doc_id),
                headers={"Authorization": f"Bearer {access_token}"},
            )
            data = resp.json()
            if data.get("code") != 0:
                return None
            doc = data.get("data", {}).get("document", {})
            return {"title": doc.get("title", ""), "owner": doc.get("owner_id", "")}
    except Exception:
        return None

# ============================================================================
# 块渲染 → Markdown
# ============================================================================

def _get_text_body(block: dict) -> Optional[dict]:
    """获取块的文本体。"""
    bt = block.get("block_type", 0)
    map = {
        BLOCK_TEXT: "text",
        BLOCK_H1: "heading1", BLOCK_H2: "heading2",
        BLOCK_H3: "heading3", BLOCK_H4: "heading4",
        BLOCK_H5: "heading5", BLOCK_H6: "heading6",
        BLOCK_H7: "heading7", BLOCK_H8: "heading8",
        BLOCK_H9: "heading9",
        BLOCK_BULLET: "bullet", BLOCK_ORDERED: "ordered",
        BLOCK_CODE: "code", BLOCK_QUOTE: "quote",
        BLOCK_TODO: "todo", BLOCK_CALLOUT: "callout",
    }
    return block.get(map.get(bt, ""))

def _render_text_elements(elements: list) -> str:
    """将飞书文本元素列表渲染为Markdown行内文本。"""
    if not elements:
        return ""
    parts = []
    for el in elements:
        if "text_run" in el:
            tr = el["text_run"]
            text = tr.get("content", "")
            if not text:
                continue
            style = tr.get("text_element_style", {})
            link_url = (style.get("link") or {}).get("url", "")
            if style.get("inline_code"):
                text = f"`{text}`"
            if style.get("bold"):
                text = f"**{text}**"
            if style.get("italic"):
                text = f"*{text}*"
            if style.get("strikethrough"):
                text = f"~~{text}~~"
            if link_url:
                text = f"[{text}]({link_url})"
            parts.append(text)
        elif "mention_user" in el:
            mu = el["mention_user"]
            name = mu.get("user_id", "")
            parts.append(f"@{name}")
        elif "mention_doc" in el:
            md = el["mention_doc"]
            title = md.get("title", "文档")
            parts.append(f"*{title}*")
        elif "equation" in el:
            eq = el["equation"].get("content", "")
            parts.append(f"`{eq}`")

    return "".join(parts)

def _render_block(block: dict, block_map: dict, indent: int = 0) -> str:
    """递归渲染单个块为Markdown。"""
    bt = block.get("block_type", 0)

    # 文本类块
    if bt in HEADING_TYPES:
        prefix = HEADING_TYPES[bt]
        body = _get_text_body(block)
        text = _render_text_elements(body.get("elements", [])) if body else ""
        return f"{prefix} {text}\n\n" if text.strip() else ""

    if bt == BLOCK_TEXT:
        body = _get_text_body(block)
        text = _render_text_elements(body.get("elements", [])) if body else ""
        children = _render_children(block.get("children", []), block_map, indent)
        prefix = "  " * indent
        return f"{prefix}{text}\n\n{children}" if text.strip() else children

    if bt == BLOCK_CODE:
        body = _get_text_body(block)
        text = _render_text_elements(body.get("elements", [])) if body else ""
        lang = ""
        style = block.get("code", {}).get("style", {})
        if style and style.get("language"):
            lang_map = {1: "python", 2: "javascript", 3: "java", 4: "go", 5: "cpp", 6: "shell"}
            lang = lang_map.get(style["language"], "")
        return f"```{lang}\n{text}\n```\n\n"

    if bt == BLOCK_QUOTE:
        body = _get_text_body(block)
        text = _render_text_elements(body.get("elements", [])) if body else ""
        return f"> {text}\n\n" if text.strip() else ""

    if bt == BLOCK_QUOTE_CONTAINER:
        children = _render_children(block.get("children", []), block_map, indent)
        lines = [f"> {l}" for l in children.split("\n") if l.strip()]
        return "\n".join(lines) + "\n\n"

    if bt == BLOCK_CALLOUT:
        body = _get_text_body(block)
        text = _render_text_elements(body.get("elements", [])) if body else ""
        children = _render_children(block.get("children", []), block_map, indent)
        return f"> **📌** {text}\n>\n{children}\n"

    # 列表
    if bt == BLOCK_BULLET:
        body = _get_text_body(block)
        text = _render_text_elements(body.get("elements", [])) if body else ""
        children = _render_children(block.get("children", []), block_map, indent + 1)
        prefix = "  " * indent
        return f"{prefix}- {text}\n{children}"

    if bt == BLOCK_ORDERED:
        body = _get_text_body(block)
        text = _render_text_elements(body.get("elements", [])) if body else ""
        children = _render_children(block.get("children", []), block_map, indent + 1)
        prefix = "  " * indent
        return f"{prefix}1. {text}\n{children}"

    if bt == BLOCK_TODO:
        body = _get_text_body(block)
        text = _render_text_elements(body.get("elements", [])) if body else ""
        done = block.get("todo", {}).get("style", {}).get("done", False)
        prefix = "  " * indent
        return f"{prefix}- [{'x' if done else ' '}] {text}\n"

    if bt == BLOCK_DIVIDER:
        return "---\n\n"

    if bt == BLOCK_IMAGE:
        img = block.get("image", {})
        token = img.get("token", "")
        if token:
            return f"![图片](feishu-image://{token})\n\n"
        return ""

    if bt == BLOCK_TABLE:
        rows = []
        cells = block.get("table", {}).get("cells", [])
        prop = block.get("table", {}).get("property", {})
        cols = prop.get("column_size", 1)
        for i in range(0, len(cells), cols):
            row_cells = cells[i:i+cols]
            row = []
            for cid in row_cells:
                cell_block = block_map.get(cid)
                if cell_block:
                    row.append(_render_children(
                        cell_block.get("children", []), block_map, 0).strip().replace("\n", " ")
                    )
                else:
                    row.append("")
            rows.append("| " + " | ".join(row) + " |")
        if rows:
            sep = "| " + " | ".join(["---"] * cols) + " |"
            rows.insert(1, sep)
            return "\n".join(rows) + "\n\n"
        return ""

    if bt == BLOCK_PAGE:
        return _render_children(block.get("children", []), block_map, indent)

    # 默认：尝试渲染子块
    return _render_children(block.get("children", []), block_map, indent)

def _render_children(child_ids: list, block_map: dict, indent: int = 0) -> str:
    """渲染子块列表。"""
    result = []
    for cid in (child_ids or []):
        child = block_map.get(cid)
        if child:
            result.append(_render_block(child, block_map, indent))
    return "".join(result)

# ============================================================================
# 图片下载
# ============================================================================

async def _resolve_images(
    content: str,
    app_id: str,
    app_secret: str,
) -> str:
    """替换 feishu-image://token 为实际图片URL。"""
    tokens = set(re.findall(r'feishu-image://([\w-]+)', content))
    if not tokens:
        return content

    access_token = await _get_tenant_token(app_id, app_secret)
    async with httpx.AsyncClient(timeout=15) as client:
        for token in tokens:
            try:
                resp = await client.get(
                    FEISHU_IMAGE_URL.format(token=token),
                    headers={"Authorization": f"Bearer {access_token}"},
                    follow_redirects=False,
                )
                if resp.status_code in (301, 302):
                    url = resp.headers.get("Location", "")
                    if url:
                        content = content.replace(f"feishu-image://{token}", url)
                elif resp.status_code == 200:
                    ct = resp.headers.get("content-type", "image/png")
                    b64 = base64.b64encode(resp.content).decode()
                    content = content.replace(
                        f"feishu-image://{token}",
                        f"data:{ct};base64,{b64}",
                    )
            except Exception:
                pass
    return content

# ============================================================================
# 主入口
# ============================================================================

async def extract_feishu(
    url: str,
    app_id: str,
    app_secret: str,
) -> dict:
    """提取飞书文档内容。

    Returns:
        {"success": bool, "title": str, "markdown": str, "error": str}
    """
    if not app_id or not app_secret:
        return {"success": False, "error": "飞书App ID/Secret未配置"}

    parsed = parse_feishu_url(url)
    if not parsed["token"]:
        return {"success": False, "error": "无法解析飞书URL"}

    try:
        # 1. 解析文档ID
        doc = await _resolve_document_id(
            parsed["token"], parsed["type"], app_id, app_secret,
        )
        doc_id = doc["document_id"]

        # 2. 并行获取元数据和文档块
        meta, blocks = await asyncio.gather(
            _fetch_doc_meta(doc_id, app_id, app_secret),
            _fetch_all_blocks(doc_id, app_id, app_secret),
        )

        # 3. 构建块映射
        block_map = {b["block_id"]: b for b in blocks}

        # 4. 渲染为Markdown
        page = [b for b in blocks if b.get("block_type") == BLOCK_PAGE]
        page_block = page[0] if page else {"children": [b["block_id"] for b in blocks if b.get("parent_id") == doc_id]}
        markdown = _render_children(
            page_block.get("children", []), block_map,
        )

        # 5. 解析图片
        markdown = await _resolve_images(markdown, app_id, app_secret)

        title = (meta or {}).get("title", "") if meta else "Untitled"

        return {
            "success": True,
            "title": title,
            "markdown": markdown.strip(),
            "author": "",
            "published": "",
            "description": "",
            "site": urlparse(url).netloc,
            "word_count": len(markdown),
            "html": "",
            "tags": [],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
