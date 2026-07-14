# html-2-md

[![Version](https://img.shields.io/badge/version-1.0.3-6366f1.svg)](https://github.com/wspmzs/one_agent/tags)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![QwenPaw](https://img.shields.io/badge/QwenPaw-Plugin-10b981.svg)](https://github.com/QwenLM/QwenPaw)
[![QwenPaw](https://img.shields.io/badge/QwenPaw-%3C%3D2.0.0-orange)](./plugin.json)

[English](./README-en.md)

将任意网页转换为干净、结构化的 Markdown —— 为 AI-Agent 和 Obsidian 笔记打造。

---

## ✨ 与 obsidian-clipper 官方插件有什么不同？

[obsidian-clipper](https://github.com/obsidianmd/obsidian-clipper) 是 Obsidian 官方的浏览器剪藏插件，所见即所得地把网页存到笔记里。`html-2-md` 则是一个面向 **Agent 自动化** 的后端工具：

|      | obsidian-clipper | html-2-md                      |
| ---- | ---------------- | ------------------------------ |
| 运行环境 | 浏览器扩展            | QwenPaw 插件（Python）             |
| 触发方式 | 手动点击剪藏           | Agent 自动调用                     |
| 核心场景 | 人阅读后存笔记          | LLM 读完后做分类/分析/写作               |
| 图片处理 | 保留远程链接           | remote / local / base64 三种策略   |
| 批量处理 | 不支持              | 5 并发批量 URL 转 Markdown          |
| 代理支持 | 走浏览器代理           | 独立 HTTP/HTTPS 代理配置             |
| 飞书文档 | 通过浏览器 DOM 抓取     | 飞书开放平台 API，结构化提取               |
| 输出格式 | Obsidian 笔记      | Markdown 文本 + YAML frontmatter |

简单来说：你用 obsidian-clipper **手动收藏一篇好文章**，用 html-2-md **让 Agent 自动把 100 篇文章存进知识库并分类归档**。

---

## 🎯 使用场景

### 1. 网页文章剪藏

Agent 定时扫描你的待读列表，自动将 URL 转为 Markdown 保存到本地指定文件夹，省去逐篇手动「另存为」。

### 2. Agent 搜索增强

Agent 通过搜索引擎获取 URL 后，调用本工具将网页转为结构化 Markdown，过滤广告、导航等噪音，以纯净正文注入 LLM 上下文，提升分析准确率。

### 3. 深度研究与写作

在研究类 Skill 中，Agent 先通过本工具将参考链接持久化到本地知识库，再基于完整存档展开深度分析、综述撰写和多源对比——确保引证可追溯、结论有依据。

---

## 📦 安装

```bash
pip install httpx beautifulsoup4 markdownify charset-normalizer pyyaml
qwenpaw plugin install D:\Project\qwenpaw-plugin-project\html-2-md
```

安装后在 **QwenPaw Console → 智能体 → 工具** 中启用 `html_2_md`。

---

## ⚙️ 配置

所有配置项在 QwenPaw WebUI 的工具配置页面中填写：

| 参数                     | 类型       | 默认值                                          | 说明                                                   |
| ---------------------- | -------- | -------------------------------------------- | ---------------------------------------------------- |
| `save_path`            | text     | `D:\OneDrive\Obsidian\...`                   | file 模式默认保存目录                                        |
| `filename_template`    | text     | `{date}-{title}.md`                          | 文件名模板，变量：`{date}`, `{title}`, `{domain}`, `{author}` |
| `yaml_fields`          | text     | `title,author,source,published,created,tags` | YAML frontmatter 字段                                  |
| `date_format_filename` | text     | `yyyymmdd`                                   | 文件名日期格式（`yyyymmdd` / `yyyy-mm-dd` / `iso`）           |
| `date_format_yaml`     | text     | `yyyy-mm-dd hh:mm:ss`                        | YAML 中时间字段格式                                         |
| `request_timeout`      | number   | 30                                           | 单次请求超时（秒），范围 5–120                                   |
| `max_batch_size`       | number   | 50                                           | 单次批量最大 URL 数                                         |
| `concurrent_limit`     | number   | 5                                            | 批量并发数                                                |
| `image_handling`       | text     | `remote`                                     | 图片策略：`remote`（保留链接）/ `local`（下载到本地）/ `base64`（嵌入）    |
| `image_save_path`      | text     | `D:\...\images\`                             | `local` 模式下图片保存目录                                    |
| `http_proxy`           | text     | 空                                            | HTTP 代理地址                                            |
| `https_proxy`          | text     | 空                                            | HTTPS 代理地址                                           |
| `feishu_app_id`        | text     | 空                                            | 飞书开放平台 App ID                                        |
| `feishu_app_secret`    | password | 空                                            | 飞书开放平台 App Secret                                    |

---

## 🔧 飞书文档配置

飞书文档由 JavaScript 动态渲染，通用 HTML 抓取无法获取完整正文和准确标题。`html-2-md` 通过**飞书开放平台 API** 直接读取文档结构：

1. 前往 [飞书开放平台](https://open.feishu.cn/app) 创建自建应用
2. 为应用开通权限：`wiki:node:read`、`docx:document:readonly`
3. 获取 **App ID** 和 **App Secret**（[官方文档：获取访问凭证](https://open.feishu.cn/document/server-docs/api-call-guide/calling-process/get-access-token)）
4. 在 QwenPaw WebUI 的工具配置中填入 `feishu_app_id` 和 `feishu_app_secret`

配置后，飞书 wiki 和文档链接会自动走 API 提取，获得准确的标题和完整正文。未配置时回退到通用 HTML 解析。

> **隐私说明**：App ID 和 App Secret 仅存储在 QwenPaw 本地配置中，不会上传到任何服务器。

---

## 🌐 HTTP/HTTPS 代理

部分网页在国内网络环境下无法直接访问，或企业内部需要通过代理访问外网。配置代理后，所有 HTTP 请求会通过代理服务器转发：

```
http_proxy:  http://127.0.0.1:7890
https_proxy: https://127.0.0.1:7890
```

填入你本地代理软件（如 Clash、v2rayN）的地址即可。留空则直连。

---

## 📝 用法

### context 模式 — 注入 LLM 上下文

```python
resp = await html_2_md(url="https://example.com", mode="context")
# resp.content[0]["text"] → Markdown 正文
# resp.content[1]["text"] → YAML 元数据
```

### file 模式 — 保存到本地

```python
resp = await html_2_md(url="https://example.com", mode="file")
# → D:\Obsidian\articles\20260701-文章标题.md
```

### 批量模式

```python
resp = await html_2_md(
    urls=["https://a.com", "https://b.com", "https://c.com"],
    mode="file",
)
# → success: 3, fail: 0
```

---

## 🏗 项目结构

```
html-2-md/
├── plugin.json              # QwenPaw 清单
├── html_2_md_plugin.py      # 入口：Plugin 类 + register()
├── html_2_md_tools.py       # 编排：参数校验 → 批量调度 → 模式路由
├── utils.py                 # 常量、配置、文件名清理、日期格式化
├── fetcher.py               # HTTP 抓取、编码检测、指数退避重试
├── parser.py                # HTML 清理、正文提取、元数据/作者/发布时间提取
├── converter.py             # HTML → Markdown 转换、图片处理、LaTeX 格式化
├── saver.py                 # YAML frontmatter 生成、文件写入
├── feishu.py                # 飞书开放平台 API：认证、文档块获取、Markdown 渲染
├── requirements.txt
└── LICENSE
```

---

## 🙏 致谢

本项目参考了以下开源项目：

- [obsidian-clipper](https://github.com/obsidianmd/obsidian-clipper) — Obsidian 官方网页剪藏插件，提供了内容提取和模板引擎的参考实现。
- [obsidian-clipper-cn](https://github.com/nextcaicai/obsidian-clipper-cn) — 中文内容增强版，其飞书 API 集成和微信公众号优化为本项目的飞书模块提供了设计参考。

---

## 📄 License

Apache 2.0 © 2026 impmzs
