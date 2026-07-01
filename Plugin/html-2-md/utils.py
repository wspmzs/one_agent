# -*- coding: utf-8 -*-
"""工具函数：常量、配置读取、路径初始化、文件名清理。"""

import re
from datetime import datetime
from qwenpaw.plugins import get_tool_config


# ============================================================================
# 常量
# ============================================================================

LAZY_IMG_ATTRS = [
    "data-src", "data-original", "data-lazy-src", "data-srcset",
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# ============================================================================
# 配置读取
# ============================================================================

_DEFAULTS = {
    "save_path": "D:\\Obsidian\\articles\\",
    "filename_template": "{date}-{title}.md",
    "yaml_fields": "title,author,source,published,created,tags",
    "request_timeout": 30,
    "max_batch_size": 50,
    "concurrent_limit": 5,
    "image_handling": "remote",
    "image_save_path": "D:\\Obsidian\\articles\\_image\\",
    "http_proxy": "",
    "https_proxy": "",
    "feishu_app_id": "",
    "feishu_app_secret": "",
    "date_format_filename": "yyyymmdd",
    "date_format_yaml": "yyyy-mm-dd hh:mm:ss",
}

def get_config() -> dict:
    """获取工具配置，带默认值。"""
    cfg = get_tool_config("html_2_md") or {}
    return {k: cfg.get(k, v) for k, v in _DEFAULTS.items()}

# ============================================================================
# 日期格式化
# ============================================================================

_DATE_FORMATS = {
    "yyyymmdd": "%Y%m%d",
    "yyyy-mm-dd": "%Y-%m-%d",
    "yyyy-mm-dd hh:mm:ss": "%Y-%m-%d %H:%M:%S",
    "iso": "%Y-%m-%dT%H:%M:%S+08:00",
}

def format_date(fmt_key: str, dt: datetime = None) -> str:
    """按配置的格式字符串格式化日期。"""
    dt = dt or datetime.now()
    py_fmt = _DATE_FORMATS.get(fmt_key, "%Y%m%d")
    return dt.strftime(py_fmt)

def normalize_date(raw: str, fmt_key: str) -> str:
    """将各种格式的日期字符串统一格式化。失败返回原始值。"""
    if not raw:
        return ""
    # 清理 HTML 实体
    import html
    cleaned = html.unescape(raw).strip()
    # 去掉子秒部分（.0000000）
    cleaned = re.sub(r'\.\d{3,}', '', cleaned)
    # 尝试多种格式解析
    for py_fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y%m%d",
    ]:
        try:
            dt = datetime.strptime(cleaned, py_fmt)
            return format_date(fmt_key, dt)
        except ValueError:
            continue
    return cleaned  # 解析失败，返回清理后的原始值

# ============================================================================
# 文件名清理
# ============================================================================

def sanitize_filename(filename: str) -> str:
    """清理文件名中的非法字符（Windows/跨平台）。"""
    result = filename.replace("\xa0", " ").replace("\u3000", " ")
    result = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", result)
    result = result.replace("#", "").replace("^", "").replace("[", "").replace("]", "")
    result = re.sub(r'\s+', ' ', result)
    result = result.strip().strip(".")
    if not result:
        return "Untitled"
    return result[:245]

def generate_image_filename(alt: str, index: int, ext: str) -> str:
    """生成图片文件名：优先alt文本，否则时间戳+序号。"""
    if alt and len(alt.strip()) >= 2:
        sanitized = sanitize_filename(alt.strip())
        if sanitized:
            return f"{sanitized}.{ext}"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}-{index:06d}.{ext}"
