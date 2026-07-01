# -*- coding: utf-8 -*-
"""转换模块：HTML→Markdown转换 + 图片处理（remote/local/base64）。"""

import base64
import os
import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md_convert

import utils
import fetcher
import feishu
import parser as html_parser


def _extract_code_lang(el) -> str:
    """从 <pre> 或 <code> 的 class 中提取语言标记。返回空串则无语言。"""
    for tag in (el, el.find("code")) if el else ():
        if tag is None:
            continue
        cls = " ".join(tag.get("class", [])) if tag.get("class") else ""
        m = re.search(r'(?:language|lang)-(\w+)', cls)
        if m:
            return m.group(1)
        # 裸类名：python, js, json, bash 等
        for bare in cls.split():
            bare = bare.strip().lower()
            if bare in ("python", "js", "javascript", "json", "bash", "shell", "sh",
                        "java", "go", "rust", "cpp", "c", "sql", "yaml", "xml",
                        "html", "css", "typescript", "ts", "markdown", "md", "text", "diff",
                        "mermaid", "plantuml", "ascii"):
                return bare
    return ""


async def fetch_and_convert(url: str, config: dict, client: httpx.AsyncClient = None) -> dict:
    """抓取网页并转换为Markdown。"""
    close_client = client is None

    # ── 飞书API路由 ──
    if feishu.is_feishu_url(url):
        app_id = config.get("feishu_app_id", "")
        app_secret = config.get("feishu_app_secret", "")
        if app_id and app_secret:
            return await feishu.extract_feishu(url, app_id, app_secret)

    if client is None:
        client = fetcher.make_client(config)

    try:
        html_bytes = await fetcher.fetch_html(client, url)
        encoding = fetcher.detect_encoding(html_bytes)
        try:
            html = html_bytes.decode(encoding or "utf-8")
        except (UnicodeDecodeError, LookupError):
            html = html_bytes.decode("utf-8", errors="replace")

        soup = BeautifulSoup(html, "html.parser")
        title = html_parser.extract_title(soup)
        author = html_parser.extract_author(soup)
        published = html_parser.extract_published(soup)
        description = html_parser.extract_meta(soup, "description")
        site = html_parser.extract_meta(soup, "og:site_name") or urlparse(url).netloc

        html_parser.clean_html(soup, url)
        body = html_parser.extract_body(soup)
        word_count = len(body.get_text(strip=True)) if body else 0
        tags = html_parser.extract_tags(soup)

        markdown = md_convert(str(body), code_language_callback=_extract_code_lang) if body else ""
        # LaTeX 转通用格式：\(..\) → $..$ , \[..\] → $$..$$
        markdown = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', markdown, flags=re.DOTALL)
        markdown = re.sub(r'\\\((.*?)\\\)', r'$\1$', markdown)
        if "github.com" in url or "gitee.com" in url:
            markdown = re.sub(r'!\[\]\([^)]*\)\s*', '', markdown)
            markdown = re.sub(r'(?<!!)\[\]\([^)]*\)\s*', '', markdown)

        markdown = await _process_images(markdown, url, config)

        return {
            "success": True, "markdown": markdown.strip(),
            "title": title, "author": author,
            "published": published, "description": description,
            "site": site, "word_count": word_count, "html": str(soup),
            "tags": tags,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if close_client and client is not None:
            await client.aclose()


async def _process_images(markdown: str, url: str, config: dict) -> str:
    strategy = config.get("image_handling", "remote")
    if strategy == "remote":
        return markdown
    if strategy == "base64":
        return await _to_base64(markdown, config)
    if strategy == "local":
        return await _to_local(markdown, config)
    return markdown


async def _to_base64(markdown: str, config: dict) -> str:
    urls = re.findall(r'!\[.*?\]\((https?://[^\s)]+)\)', markdown)
    if not urls:
        return markdown
    async with httpx.AsyncClient(
        timeout=config.get("request_timeout", 30),
        headers={"User-Agent": utils.USER_AGENT},
    ) as client:
        for img_url in urls:
            try:
                resp = await client.get(img_url)
                if resp.status_code == 200:
                    ct = resp.headers.get("content-type", "image/png")
                    b64 = base64.b64encode(resp.content).decode()
                    markdown = markdown.replace(img_url, f"data:{ct};base64,{b64}")
            except Exception:
                pass
    return markdown


async def _to_local(markdown: str, config: dict) -> str:
    save_path = config.get("image_save_path", "")
    os.makedirs(save_path, exist_ok=True)

    async with httpx.AsyncClient(
        timeout=config.get("request_timeout", 30),
        headers={"User-Agent": utils.USER_AGENT},
    ) as client:
        for idx, match in enumerate(re.finditer(r'!\[(.*?)\]\((https?://[^\s)]+)\)', markdown), 1):
            alt = match.group(1).strip()
            img_url = match.group(2)
            try:
                resp = await client.get(img_url)
                if resp.status_code != 200:
                    continue
                ct = resp.headers.get("content-type", "image/png")
                ext = ct.split("/")[-1].split(";")[0] or "png"
                fname = utils.generate_image_filename(alt, idx, ext)
                fpath = os.path.join(save_path, fname)
                with open(fpath, "wb") as f:
                    f.write(resp.content)
                markdown = markdown.replace(img_url, fpath)
            except Exception:
                pass
    return markdown
