# -*- coding: utf-8 -*-
"""存盘模块：YAML生成、文件写入、文件名模板。"""

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import yaml

import utils


async def save_to_file(result: dict, url: str, save_path: str,
                       filename_template: str, yaml_fields: list, config: dict) -> str:
    """生成带YAML frontmatter的Markdown文件并保存。"""
    now = datetime.now()
    var_map = {
        "date": utils.format_date(config.get("date_format_filename", "yyyymmdd"), now),
        "title": result.get("title", "Untitled"),
        "domain": urlparse(url).netloc,
        "author": result.get("author", ""),
    }
    filename = filename_template
    for key, val in var_map.items():
        filename = filename.replace("{" + key + "}", utils.sanitize_filename(val))
    filename = filename.replace("/", "-").replace("\\", "-")

    save_dir = Path(save_path)
    save_dir.mkdir(parents=True, exist_ok=True)
    filepath = save_dir / filename

    frontmatter = build_frontmatter(result, url, yaml_fields, config)
    filepath.write_text(f"{frontmatter}\n\n{result['markdown']}", encoding="utf-8")
    return str(filepath)


def build_frontmatter(result: dict, url: str, yaml_fields: list, config: dict) -> str:
    """构建YAML前置元数据。字段顺序固定：title, author, source, published, created, tags。"""
    now = datetime.now()
    fmt = config.get("date_format_yaml", "yyyy-mm-dd hh:mm:ss")
    data = {}

    if "title" in yaml_fields:
        data["title"] = result.get("title", "")
    if "author" in yaml_fields:
        data["author"] = result.get("author", "")
    if "source" in yaml_fields:
        data["source"] = url
    if "published" in yaml_fields:
        data["published"] = utils.normalize_date(result.get("published", ""), fmt) or ""
    if "created" in yaml_fields:
        data["created"] = utils.format_date(fmt, now)
    if "tags" in yaml_fields:
        data["tags"] = result.get("tags", [])

    yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return f"---\n{yaml_str}---"
