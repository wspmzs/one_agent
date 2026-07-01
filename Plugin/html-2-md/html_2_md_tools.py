# -*- coding: utf-8 -*-
"""HTML转Markdown Tool函数入口。"""

import asyncio
from typing import List

import utils
import fetcher
import converter
import saver

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse


async def html_2_md(
    url: str = None,
    urls: List[str] = None,
    mode: str = "context",
    save_path: str = None,
    filename_template: str = None,
    yaml_fields: str = None,
) -> ToolResponse:
    """将网页URL转换为Markdown。

    Args:
        url: 单个网页URL（与urls二选一）。
        urls: URL数组（仅file模式）。
        mode: "context"返回MD，"file"保存到文件。
        save_path: file模式保存目录。
        filename_template: 文件名模板。
        yaml_fields: 逗号分隔的YAML字段名。
    """
    if not url and not urls:
        return ToolResponse(content=[TextBlock(type="text", text="[FAIL] 请提供 url 或 urls 参数")])
    if url and urls:
        return ToolResponse(content=[TextBlock(type="text", text="[FAIL] url 和 urls 不能同时提供")])
    if urls and mode == "context":
        return ToolResponse(content=[TextBlock(type="text", text="[FAIL] 批量模式仅支持 mode='file'")])

    config = utils.get_config()
    _save_path = save_path or config["save_path"]
    _filename_template = filename_template or config["filename_template"]
    _yaml_fields = (yaml_fields or config["yaml_fields"]).split(",")

    if urls:
        return await _batch(urls, _save_path, _filename_template, _yaml_fields, config)

    client = fetcher.make_client(config)
    try:
        result = await converter.fetch_and_convert(url, config, client)
    finally:
        await client.aclose()

    if not result["success"]:
        return ToolResponse(content=[TextBlock(type="text", text=f"[FAIL] {url}: {result['error']}")])

    if mode == "context":
        frontmatter = saver.build_frontmatter(result, url, _yaml_fields, config)
        return ToolResponse(content=[
            TextBlock(type="text", text=result["markdown"]),
            TextBlock(type="text", text=frontmatter),
        ])

    file_path = await saver.save_to_file(result, url, _save_path, _filename_template, _yaml_fields, config)
    return ToolResponse(content=[TextBlock(type="text", text=(
        f"[OK] 保存成功\nfile_path: {file_path}\ntitle: {result.get('title', '')}\nurl: {url}"
    ))])


async def _batch(urls, save_path, filename_template, yaml_fields, config):
    max_batch = config.get("max_batch_size", 50)
    limit = config.get("concurrent_limit", 5)
    if len(urls) > max_batch:
        return ToolResponse(content=[TextBlock(type="text",
            text=f"[FAIL] URL数量({len(urls)})超过最大限制({max_batch})")])

    sem = asyncio.Semaphore(limit)

    async def _one(u):
        async with sem:
            client = fetcher.make_client(config)
            try:
                r = await converter.fetch_and_convert(u, config, client)
            finally:
                await client.aclose()
            if not r["success"]:
                return {"url": u, "success": False, "error": r["error"]}
            fp = await saver.save_to_file(r, u, save_path, filename_template, yaml_fields, config)
            return {"url": u, "success": True, "file_path": fp, "title": r.get("title", "")}

    results = await asyncio.gather(*[_one(u) for u in urls])
    ok = sum(1 for r in results if r["success"])
    lines = [f"[OK] 批量处理完成\ntotal: {len(results)}\nsuccess: {ok}\nfail: {len(results) - ok}"]
    for r in results:
        if r["success"]:
            lines.append(f"\n  [OK] {r['url']}\n    -> {r['file_path']}")
        else:
            lines.append(f"\n  [FAIL] {r['url']}: {r['error']}")
    return ToolResponse(content=[TextBlock(type="text", text="".join(lines))])
