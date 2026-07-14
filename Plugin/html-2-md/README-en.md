# html-2-md

[![Version](https://img.shields.io/badge/version-1.0.2-6366f1.svg)](https://github.com/wspmzs/one_agent/tags)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![QwenPaw](https://img.shields.io/badge/QwenPaw-Plugin-10b981.svg)](https://github.com/QwenLM/QwenPaw)
[![QwenPaw](https://img.shields.io/badge/QwenPaw-%3C%3D2.0.0-orange)](./plugin.json)

[中文](./README.md)

Convert any web page into clean, structured Markdown — built for AI agents and Obsidian vaults.

---

## ✨ How is this different from obsidian-clipper?

[obsidian-clipper](https://github.com/obsidianmd/obsidian-clipper) is the official Obsidian browser extension for manual web clipping. `html-2-md` is a **backend tool built for agent automation**:

|                  | obsidian-clipper       | html-2-md                                           |
| ---------------- | ---------------------- | --------------------------------------------------- |
| Runtime          | Browser extension      | QwenPaw plugin (Python)                             |
| Trigger          | Manual click           | Agent-driven invocation                             |
| Primary use case | Save for human reading | LLM ingestion → classification / analysis / writing |
| Image handling   | Remote URLs only       | `remote` / `local` / `base64`                       |
| Batch processing | Not supported          | 5 concurrent batch URL → Markdown                   |
| Proxy support    | Via browser proxy      | Standalone HTTP/HTTPS proxy config                  |
| Feishu docs      | Browser DOM scraping   | Feishu Open Platform API — structured extraction    |
| Output format    | Obsidian note          | Markdown text + YAML frontmatter                    |

In short: you use obsidian-clipper to **manually save a great article**, and html-2-md to **have an agent automatically archive and classify 100 articles into your knowledge base**.

---

## 🎯 Use Cases

### 1. Web Article Clipping

Agents scan your reading list on a schedule, converting URLs to Markdown and saving them to local folders — no more manual "Save As" for each article.

### 2. Agent Search Enhancement

After an agent retrieves URLs from a search engine, this tool strips ads, navigation, and other noise, delivering clean Markdown into the LLM context for more accurate analysis.

### 3. Deep Research & Writing

In research-oriented Skills, the agent first persists reference links to a local knowledge base via this tool, then conducts in-depth analysis, synthesis, and multi-source comparison — ensuring every citation is traceable and every conclusion is grounded.

---

## 📦 Installation

```bash
pip install httpx beautifulsoup4 markdownify charset-normalizer pyyaml
qwenpaw plugin install D:\Project\qwenpaw-plugin-project\html-2-md
```

Enable `html_2_md` in **QwenPaw Console → Agents → Tools** after installation.

---

## ⚙️ Configuration

All settings are available in the QwenPaw WebUI tool config panel:

| Parameter              | Type     | Default                                      | Description                                            |
| ---------------------- | -------- | -------------------------------------------- | ------------------------------------------------------ |
| `save_path`            | text     | `D:\OneDrive\Obsidian\...`                   | File mode default output directory                     |
| `filename_template`    | text     | `{date}-{title}.md`                          | Variables: `{date}`, `{title}`, `{domain}`, `{author}` |
| `yaml_fields`          | text     | `title,author,source,published,created,tags` | YAML frontmatter fields                                |
| `date_format_filename` | text     | `yyyymmdd`                                   | Date format for filenames                              |
| `date_format_yaml`     | text     | `yyyy-mm-dd hh:mm:ss`                        | Date format in YAML metadata                           |
| `request_timeout`      | number   | 30                                           | Request timeout in seconds (5–120)                     |
| `max_batch_size`       | number   | 50                                           | Max URLs per batch (1–200)                             |
| `concurrent_limit`     | number   | 5                                            | Concurrent requests (1–20)                             |
| `image_handling`       | text     | `remote`                                     | `remote` / `local` / `base64`                          |
| `image_save_path`      | text     | `D:\...\images\`                             | Local image download directory                         |
| `http_proxy`           | text     | (empty)                                      | HTTP proxy URL                                         |
| `https_proxy`          | text     | (empty)                                      | HTTPS proxy URL                                        |
| `feishu_app_id`        | text     | (empty)                                      | Feishu Open Platform App ID                            |
| `feishu_app_secret`    | password | (empty)                                      | Feishu Open Platform App Secret                        |

---

## 🔧 Feishu Document Setup

Feishu documents are SPAs — content is rendered by JavaScript, making generic HTML extraction unreliable. `html-2-md` uses the **Feishu Open Platform API** for structured document access:

1. Go to [Feishu Open Platform](https://open.feishu.cn/app) and create a custom app
2. Grant permissions: `docx:document:readonly`, `wiki:node:read`
3. Obtain your **App ID** and **App Secret** ([docs: Get access token](https://open.feishu.cn/document/server-docs/api-call-guide/calling-process/get-access-token))
4. Fill in `feishu_app_id` and `feishu_app_secret` in the QwenPaw WebUI tool config

Once configured, Feishu wiki and doc links are routed to the API for accurate titles and complete content. Falls back to generic HTML parsing when not configured.

> **Privacy**: App ID and App Secret are stored locally in QwenPaw's config and never uploaded to any server.

---

## 🌐 HTTP/HTTPS Proxy

Some pages may be inaccessible from certain network environments, or corporate networks may require a proxy to reach external services. Set up proxy config to route HTTP requests through your proxy server:

```
http_proxy:  http://127.0.0.1:7890
https_proxy: https://127.0.0.1:7890
```

Fill in your local proxy address (Clash, v2rayN, etc.). Leave empty for direct connection.

---

## 📝 Usage

### Context mode — feed Markdown to your LLM

```python
resp = await html_2_md(url="https://example.com", mode="context")
# resp.content[0]["text"] → Markdown body
# resp.content[1]["text"] → YAML metadata
```

### File mode — save to disk

```python
resp = await html_2_md(url="https://example.com", mode="file")
# → D:\Obsidian\articles\20260701-Article-Title.md
```

### Batch mode

```python
resp = await html_2_md(
    urls=["https://a.com", "https://b.com", "https://c.com"],
    mode="file",
)
# → success: 3, fail: 0
```

---

## 🏗 Architecture

```
html-2-md/
├── plugin.json              # QwenPaw manifest
├── html_2_md_plugin.py      # Entry: Plugin class + register()
├── html_2_md_tools.py       # Orchestrator: validation → batch dispatch → mode routing
├── utils.py                 # Constants, config, filename sanitizer, date formatter
├── fetcher.py               # HTTP fetch, encoding detection, exponential backoff retry
├── parser.py                # HTML cleanup, body extraction, metadata / author / publish date
├── converter.py             # HTML → Markdown, image processing, LaTeX formatting
├── saver.py                 # YAML frontmatter generation, file I/O
├── feishu.py                # Feishu Open API: auth, block fetch, Markdown renderer
├── requirements.txt
└── LICENSE
```

Each module is under 150 lines with a single responsibility.

---

## 🙏 Acknowledgments

This project draws inspiration from:

- [obsidian-clipper](https://github.com/obsidianmd/obsidian-clipper) — Obsidian's official web clipper, which provided the reference implementation for content extraction and template engine.
- [obsidian-clipper-cn](https://github.com/nextcaicai/obsidian-clipper-cn) — Chinese content enhanced fork, whose Feishu API integration and WeChat article optimization informed the design of our Feishu module.

---

## 📄 License

Apache 2.0 © 2026 impmzs
