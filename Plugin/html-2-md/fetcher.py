# -*- coding: utf-8 -*-
"""HTTP抓取模块：网页下载、编码检测、重试策略。"""

import asyncio
import re
from typing import Optional

import httpx
import utils


async def fetch_html(client: httpx.AsyncClient, url: str, max_retries: int = 2) -> bytes:
    """抓取网页HTML，含指数退避重试（超时/5xx重试，4xx不重试）。"""
    for attempt in range(max_retries + 1):
        try:
            response = await client.get(url)
            if response.status_code < 500:
                response.raise_for_status()
                return response.content
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
                continue
            response.raise_for_status()
        except (httpx.TimeoutException, httpx.ConnectError):
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
                continue
            raise
    return b""


def detect_encoding(content: bytes) -> Optional[str]:
    """检测页面编码（meta标签 > charset-normalizer > utf-8兜底）。"""
    try:
        head = content[:2048]
        match = re.search(rb'<meta[^>]+charset=["\']?([^"\'>\s]+)', head, re.IGNORECASE)
        if match:
            return match.group(1).decode("ascii", errors="replace")
        try:
            from charset_normalizer import detect
            result = detect(content)
            if result and result.get("encoding"):
                return result["encoding"]
        except ImportError:
            pass
    except Exception:
        pass
    return "utf-8"


def make_client(config: dict) -> httpx.AsyncClient:
    """创建带代理和超时的 httpx 客户端。"""
    proxy = (config.get("https_proxy") or config.get("http_proxy") or "").strip()
    return httpx.AsyncClient(
        proxy=proxy if proxy else None,
        timeout=config.get("request_timeout", 30),
        follow_redirects=True,
        headers={"User-Agent": utils.USER_AGENT},
    )
