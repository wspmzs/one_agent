# -*- coding: utf-8 -*-
"""Pexels Image Search 工具函数。"""

import os
import json
import logging
from datetime import datetime, timezone

import httpx
from agentscope.message import TextBlock
from agentscope.tool import ToolResponse
from qwenpaw.plugins import get_tool_config

logger = logging.getLogger(__name__)

PEXELS_PHOTO_SEARCH_URL = "https://api.pexels.com/v1/search"
PEXELS_PHOTO_URL = "https://api.pexels.com/v1/photos"

SIZE_LABELS = {
    "original": "原始尺寸",
    "large2x": "大图 2x",
    "large": "大图 (940px宽)",
    "medium": "中等 (350px高)",
    "small": "小图 (130px高)",
    "portrait": "竖版 (800×1200)",
    "landscape": "横版 (1200×627)",
    "tiny": "缩略图 (280×200)",
}


def _get_default_config(config_name: str):
    """读取 Tool 配置，未配置时返回空 dict。"""
    cfg = get_tool_config(config_name)
    if cfg is None:
        cfg = {}
    return cfg


def _format_photo(photo: dict, preferred_size: str) -> str:
    """格式化单张图片信息为 Markdown 文本。"""
    pid = photo.get("id", "?")
    alt = photo.get("alt", "无描述")
    photographer = photo.get("photographer", "未知")
    photographer_url = photo.get("photographer_url", "")
    width = photo.get("width", 0)
    height = photo.get("height", 0)
    avg_color = photo.get("avg_color", "#000000")
    url_pexels = photo.get("url", "")
    src = photo.get("src", {})

    lines = [f"### \U0001f4f7 {pid} — {alt}"]
    lines.append(f"- **摄影师**: {photographer}")
    if photographer_url:
        lines.append(f"- **摄影师主页**: {photographer_url}")
    lines.append(f"- **尺寸**: {width}\u00d7{height} | **主色**: `{avg_color}`")
    lines.append(f"- **Pexels 页面**: {url_pexels}")
    lines.append("")
    lines.append("**可用的图片链接:**")

    # 按优先级列出所有尺寸
    size_order = ["original", "large2x", "large", "medium", "small",
                  "portrait", "landscape", "tiny"]
    for size_key in size_order:
        size_url = src.get(size_key, "")
        if size_url:
            label = SIZE_LABELS.get(size_key, size_key)
            marker = "\u2b50 默认推荐" if size_key == preferred_size else ""
            lines.append(f"  - `{size_key}`: {label} {marker}")

    lines.append("")
    lines.append(f"> \u00a9 Photo by {photographer} on Pexels (免费使用，署名建议)")
    return "\n".join(lines)


async def search_pexels_images(
    query: str,
    orientation: str = "",
    size: str = "",
    color: str = "",
    locale: str = "",
    page: int = 1,
) -> ToolResponse:
    """搜索 Pexels 高质量图片。

    Args:
        query: 搜索关键词（必填），例如 "nature landscape"、"office workspace"
        orientation: 图片方向，可选 landscape / portrait / square
        size: 图片尺寸，可选 large / medium / small
        color: 主色调，可选 red/orange/yellow/green/turquoise/blue/violet/pink/brown/black/gray/white 或 hex 值
        locale: 语言区域，例如 zh-CN、en-US、ja-JP
        page: 页码，从 1 开始

    Returns:
        ToolResponse: 结构化图片搜索结果，含 URL、尺寸、摄影师署名
    """
    # --- 输入校验 ---
    if not query or not query.strip():
        return ToolResponse(content=[
            TextBlock(type="text", text="Error: query 参数不能为空，请提供搜索关键词。")
        ])

    # --- 读取配置 ---
    cfg = _get_default_config("search_pexels_images")
    token = cfg.get("pexels_token", "")
    if not token:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text="Error: 未配置 Pexels API Token。\n"
                           "请在 QwenPaw Web UI → Agent Settings → Tools → "
                           "search_pexels_images → 配置 pexels_token。\n"
                           "免费获取: https://www.pexels.com/api/")
        ])

    per_page = int(cfg.get("results_per_page", 5))
    preferred_size = cfg.get("preferred_image_size", "large")

    # --- 构建请求 ---
    params = {
        "query": query.strip(),
        "per_page": str(per_page),
        "page": str(page),
    }
    if orientation:
        params["orientation"] = orientation
    if size:
        params["size"] = size
    if color:
        params["color"] = color
    if locale:
        params["locale"] = locale

    headers = {
        "Authorization": token,
        "Accept": "application/json",
    }

    # --- 调 API ---
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(PEXELS_PHOTO_SEARCH_URL, params=params,
                                    headers=headers)
    except httpx.TimeoutException:
        return ToolResponse(content=[
            TextBlock(type="text", text="Error: Pexels API 请求超时，请稍后重试。")
        ])
    except httpx.RequestError as e:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text=f"Error: Pexels API 网络请求失败: {e}")
        ])

    if resp.status_code == 401:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text="Error: Pexels API Token 无效 (401)。\n"
                           "请检查 pexels_token 配置是否正确。")
        ])
    if resp.status_code == 429:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text="Error: Pexels API 速率限制 (429)，请稍后再试。\n"
                           "免费账户: 200 请求/小时, 20,000 请求/月。")
        ])
    if resp.status_code != 200:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text=f"Error: Pexels API 返回错误 (HTTP {resp.status_code}): "
                           f"{resp.text[:500]}")
        ])

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return ToolResponse(content=[
            TextBlock(type="text", text="Error: Pexels API 返回数据解析失败。")
        ])

    photos = data.get("photos", [])
    total_results = data.get("total_results", 0)
    current_page = data.get("page", page)
    total_pages = (total_results + per_page - 1) // per_page if total_results else 0

    if not photos:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text=f"\U0001f50d 搜索 \"{query.strip()}\" 无结果。\n"
                           "建议: 尝试更宽泛的关键词或英文搜索。")
        ])

    # --- 格式化输出 ---
    lines = [
        f"## \U0001f50d Pexels 图片搜索: \"{query.strip()}\"",
        f"共 {total_results} 张 | 第 {current_page}/{total_pages} 页 | "
        f"每页 {len(photos)} 张",
        f"默认尺寸: {SIZE_LABELS.get(preferred_size, preferred_size)}",
    ]

    # 速率限制信息
    rate_limit = resp.headers.get("X-Ratelimit-Limit", "")
    rate_remaining = resp.headers.get("X-Ratelimit-Remaining", "")
    if rate_remaining:
        lines.append(f"\U0001f6a6 速率限制: 剩余 {rate_remaining}/{rate_limit} 次/小时")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, photo in enumerate(photos, 1):
        lines.append(f"### \U0001f4f7 {i}. {photo.get('alt', '无描述')}")
        lines.append("")
        lines.append("| 属性 | 值 |")
        lines.append("|------|-----|")
        lines.append(f"| ID | `{photo.get('id', '?')}` |")
        lines.append(f"| 摄影师 | {photo.get('photographer', '未知')} |")
        if photo.get("photographer_url"):
            lines.append(f"| 摄影师主页 | {photo.get('photographer_url')} |")
        lines.append(f"| 尺寸 | {photo.get('width', 0)}\u00d7{photo.get('height', 0)} |")
        lines.append(f"| 主色 | `{photo.get('avg_color', '#000000')}` |")
        lines.append(f"| Pexels 页面 | {photo.get('url', '')} |")
        lines.append("")

        src = photo.get("src", {})
        lines.append("**可用的图片链接:**")
        lines.append("")
        size_order = ["original", "large2x", "large", "medium", "small",
                      "portrait", "landscape", "tiny"]
        for size_key in size_order:
            size_url = src.get(size_key, "")
            if size_url:
                label = SIZE_LABELS.get(size_key, size_key)
                marker = "  \u2b50 默认推荐" if size_key == preferred_size else ""
                lines.append(f"- `{size_key}`: [{label}]({size_url}){marker}")

        lines.append("")
        lines.append(f"> \u00a9 Photo by {photo.get('photographer', '未知')} on Pexels "
                     "(免费使用，建议署名)")
        lines.append("")
        lines.append("---")
        lines.append("")

    # 使用提示
    lines.append("### \u0001f4a1 使用提示")
    lines.append(f"- AI 默认使用 `{preferred_size}` 尺寸，如需其他尺寸请自行选择")
    lines.append("- 下载图片: 调用 `download_pexels_image` 并传入 `photo_id`")
    lines.append("- PPT 嵌入: 将 URL 直接粘贴到图片地址栏")
    lines.append("- 网页嵌入: `<img src=\"URL\" alt=\"描述\">`")
    lines.append("- 署名建议: 附上 \"Photo by [摄影师] on Pexels\"")

    return ToolResponse(content=[TextBlock(type="text", text="\n".join(lines))])


async def download_pexels_image(
    photo_id: int,
    output_dir: str = "",
    size: str = "",
) -> ToolResponse:
    """下载 Pexels 图片到本地。

    Args:
        photo_id: Pexels 图片 ID（必填），从 search_pexels_images 结果中获取
        output_dir: 保存目录，默认为系统临时目录
        size: 图片尺寸，默认为配置中的 preferred_image_size，可选 original/large2x/large/medium/small/portrait/landscape/tiny

    Returns:
        ToolResponse: 本地文件路径 + 摄影师署名信息
    """
    # --- 输入校验 ---
    if not photo_id or photo_id <= 0:
        return ToolResponse(content=[
            TextBlock(type="text", text="Error: photo_id 无效，请提供有效的图片 ID。")
        ])

    # --- 读取配置 ---
    cfg = _get_default_config("download_pexels_image")
    token = cfg.get("pexels_token", "")
    if not token:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text="Error: 未配置 Pexels API Token。\n"
                           "请在 QwenPaw Web UI → Agent Settings → Tools → "
                           "download_pexels_image → 配置 pexels_token。")
        ])

    # 尺寸优先级: 函数参数 > 搜索配置中的 preferred_image_size > 默认 large
    if not size:
        search_cfg = _get_default_config("search_pexels_images")
        size = search_cfg.get("preferred_image_size", "large")

    # 输出目录
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "downloads")
    os.makedirs(output_dir, exist_ok=True)

    # --- 第一步: 获取图片元数据 ---
    headers = {
        "Authorization": token,
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{PEXELS_PHOTO_URL}/{photo_id}",
                                    headers=headers)
    except httpx.TimeoutException:
        return ToolResponse(content=[
            TextBlock(type="text", text="Error: Pexels API 请求超时，请稍后重试。")
        ])
    except httpx.RequestError as e:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text=f"Error: Pexels API 网络请求失败: {e}")
        ])

    if resp.status_code == 404:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text=f"Error: 图片 ID={photo_id} 不存在 (404)。")
        ])
    if resp.status_code == 401:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text="Error: Pexels API Token 无效 (401)。")
        ])
    if resp.status_code != 200:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text=f"Error: Pexels API 返回错误 (HTTP {resp.status_code})。")
        ])

    try:
        photo = resp.json()
    except json.JSONDecodeError:
        return ToolResponse(content=[
            TextBlock(type="text", text="Error: Pexels API 返回数据解析失败。")
        ])

    src = photo.get("src", {})
    download_url = src.get(size, "")
    if not download_url:
        # 降级: 用第一个可用的尺寸
        for fallback in ["large", "original", "large2x", "medium",
                         "small", "portrait", "landscape", "tiny"]:
            download_url = src.get(fallback, "")
            if download_url:
                size = fallback
                break

    if not download_url:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text=f"Error: 图片 ID={photo_id} 无可下载的 URL。")
        ])

    # --- 第二步: 下载文件 ---
    ext = ".jpg"
    if "?" in download_url:
        # URL 带参数时从路径提取扩展名
        path_part = download_url.split("?")[0]
        _, ext_part = os.path.splitext(path_part)
        if ext_part:
            ext = ext_part

    filename = f"pexels-{photo_id}-{size}{ext}"
    filepath = os.path.join(output_dir, filename)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            dl_resp = await client.get(download_url, headers=headers,
                                       follow_redirects=True)
    except httpx.TimeoutException:
        return ToolResponse(content=[
            TextBlock(type="text", text="Error: 图片下载超时 (60s)。")
        ])
    except httpx.RequestError as e:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text=f"Error: 图片下载失败: {e}")
        ])

    if dl_resp.status_code != 200:
        return ToolResponse(content=[
            TextBlock(type="text",
                      text=f"Error: 图片下载失败 (HTTP {dl_resp.status_code})。")
        ])

    with open(filepath, "wb") as f:
        f.write(dl_resp.content)

    file_size_kb = len(dl_resp.content) / 1024

    # --- 格式化输出 ---
    photographer = photo.get("photographer", "未知")
    photographer_url = photo.get("photographer_url", "")
    alt = photo.get("alt", "无描述")
    width = photo.get("width", 0)
    height = photo.get("height", 0)
    avg_color = photo.get("avg_color", "#000000")

    lines = [
        f"## \u2705 图片下载完成",
        "",
        f"**文件路径**: `{filepath}`",
        f"**文件大小**: {file_size_kb:.1f} KB",
        f"**尺寸**: {width}\u00d7{height}",
        f"**主色**: `{avg_color}`",
        f"**描述**: {alt}",
        "",
        f"**摄影师**: {photographer}",
    ]
    if photographer_url:
        lines.append(f"**摄影师主页**: {photographer_url}")
    lines.append(f"**Pexels 页面**: {photo.get('url', '')}")
    lines.append("")
    lines.append("### \u00a9 署名信息")
    lines.append(f"> Photo by {photographer} on Pexels (免费使用，建议署名)")
    lines.append(f"```html")
    lines.append(f'<a href="{photo.get("url", "")}">Photo</a> '
                 f'by <a href="{photographer_url}">{photographer}</a> '
                 f'on <a href="https://www.pexels.com">Pexels</a>')
    lines.append(f"```")

    return ToolResponse(content=[TextBlock(type="text", text="\n".join(lines))])
