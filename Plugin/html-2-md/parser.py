# -*- coding: utf-8 -*-
"""HTML解析模块：元素清理、正文提取、元数据提取。"""

import json
import re
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import utils


BODY_SELECTORS = [
    "article", '[role="main"]', "main",
    ".post-content", ".article-content", ".entry-content",
    "#js_content", ".markdown-body", "#readability-content",
]

# ── 清理 ──

def clean_html(soup: BeautifulSoup, base_url: str):
    for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    for img in soup.find_all("img"):
        for attr in utils.LAZY_IMG_ATTRS:
            if img.get(attr):
                img["src"] = img[attr]
                break
        src = img.get("src", "")
        if src and not src.startswith(("http://", "https://", "data:")):
            try:
                img["src"] = urljoin(base_url, src)
            except Exception:
                pass

# ── 正文 ──

def extract_body(soup: BeautifulSoup) -> Optional[BeautifulSoup]:
    for sel in BODY_SELECTORS:
        body = soup.select_one(sel)
        if body:
            return body
    return soup.body or soup

# ── 标题 ──

def extract_title(soup: BeautifulSoup) -> str:
    if soup.title and soup.title.get_text(strip=True):
        raw = soup.title.get_text(strip=True)
        m = re.match(r'^(.+?)\s+at\s+\S+\s+·\s+(.+?)\s+·\s+GitHub$', raw)
        if m:
            repo = m.group(2).replace("/", "-")
            filename = m.group(1).rsplit("/", 1)[-1]
            for ext in (".md", ".py", ".js", ".ts", ".go", ".rs", ".java"):
                if filename.endswith(ext):
                    filename = filename[:-len(ext)]
                    break
            return f"{repo}-{filename}"
        return raw
    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content", "").strip():
        return og_title["content"].strip()
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    return "Untitled"

# ── 发布时间（通用，按标准降级） ──

def extract_published(soup: BeautifulSoup) -> str:
    """通用发布时间提取。按标准降级：
    JSON-LD > <time>/<relative-time> > 微数据 > meta > 常见class。
    """
    # 1. JSON-LD（schema.org标准，博客/技术站点最可靠）
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, list):
                data = data[0] if data else {}
            for key in ("datePublished", "dateModified", "dateCreated"):
                if data.get(key):
                    return str(data[key])
        except Exception:
            pass

    # 2. HTML5 <time> 或 GitHub 的 <relative-time>
    for tag_name in ("time", "relative-time"):
        for el in soup.find_all(tag_name):
            dt = el.get("datetime", "")
            if dt:
                return dt

    # 3. Schema.org 微数据 itemprop="datePublished" 等
    for el in soup.find_all(attrs={"itemprop": True}):
        prop = (el.get("itemprop") or "").lower()
        content = el.get("content") or el.get("datetime") or el.get_text(strip=True)
        if "date" in prop and content:
            return content

    # 4. meta 标签
    for name in ("article:published_time", "date", "pubdate", "parsely-pub-date",
                 "publishdate", "dc.date", "dcterms.date"):
        val = extract_meta(soup, name)
        if val:
            return val

    # 5. 常见日期 class（掘金 .time 等）
    for cls in ("time", "publish-time", "article-time", "post-date", "date"):
        el = soup.find(class_=cls)
        if el:
            txt = el.get_text(strip=True)
            if txt and any(c.isdigit() for c in txt):
                return txt

    return ""

# ── 元数据 ──

def extract_author(soup: BeautifulSoup) -> str:
    """提取作者。meta > JSON-LD > 常见class。"""
    # meta
    for name in ("author", "article:author", "og:article:author"):
        val = extract_meta(soup, name)
        if val:
            return val
    # JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, list):
                data = data[0] if data else {}
            author = data.get("author")
            if isinstance(author, dict):
                return author.get("name", "")
            if isinstance(author, str):
                return author
            if isinstance(author, list) and author:
                a = author[0]
                return a.get("name", "") if isinstance(a, dict) else str(a)
        except Exception:
            pass
    # 常见class
    for cls in ("post-meta-author", "author-name", "post-author", "byline"):
        el = soup.find(class_=cls)
        if el:
            txt = el.get_text(strip=True)
            if txt:
                return txt
    return ""

def extract_meta(soup: BeautifulSoup, name: str) -> str:
    for attrs, key in [
        ({"name": name}, "content"),
        ({"property": name}, "content"),
        ({"property": f"og:{name}"}, "content"),
    ]:
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get(key):
            return tag[key].strip()
    return ""

def extract_tags(soup: BeautifulSoup, user_tags: list = None) -> list:
    if user_tags:
        return user_tags
    tags = []
    kw = soup.find("meta", attrs={"name": "keywords"})
    if kw and kw.get("content"):
        tags.extend(t.strip() for t in kw["content"].split(","))
    for meta in soup.find_all("meta"):
        if "tag" in (meta.get("property", "") or "").lower():
            c = meta.get("content", "").strip()
            if c:
                tags.append(c)
    return list(set(filter(None, tags))) or []
