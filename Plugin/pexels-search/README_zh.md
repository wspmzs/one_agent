# 🔍 Pexels 图片搜索 — QwenPaw 插件

[![版本](https://img.shields.io/badge/version-1.0.1-blue)](./plugin.json)
[![协议](https://img.shields.io/badge/license-Apache%202.0-green)](./LICENSE)
[![QwenPaw](https://img.shields.io/badge/QwenPaw-%3C%3D2.0.0-orange)](./plugin.json)

QwenPaw 的 Pexels 图片搜索插件🔍 。支持自然语言搜索高质量免费图片，可按方向、尺寸、颜色、语言过滤；支持 8 种分辨率直接下载。适合 Agent 自动化制作 PPT、前端页面配图、内容生成等场景。Token 通过 Web UI 安全配置，无需在代码中暴露。基于 Pexels API，免费额度 200 次/小时。

---

## 📑 目录

- [✨ 特性](#-特性)
- [📦 安装](#-安装)
- [⚙️ 配置](#️-配置)
- [🚀 使用示例](#-使用示例)
- [🖼️ 可用图片尺寸](#️-可用图片尺寸)
- [🎛️ 搜索参数](#️-搜索参数)
- [📁 项目结构](#-项目结构)
- [⏱️ 速率限制](#️-速率限制)
- [❓ 常见问题](#-常见问题)
- [📄 许可](#-许可)

---

## ✨ 特性

- **🔎 智能搜索** — 自然语言搜索，支持方向、尺寸、颜色、语言区域过滤
- **📥 本地下载** — 将任意图片下载到本地，离线使用
- **🎨 多尺寸** — 从 `tiny` 缩略图到 `original` 原始画质共 8 种分辨率
- **📊 丰富元数据** — 每张图附带摄影师、尺寸、主色调及 Pexels 页面链接
- **🔐 安全配置** — API Token 通过 QwenPaw Web UI 管理，代码中不留痕
- **📉 配额可见** — 搜索结果中显示剩余请求配额，防止超额

---

## 📦 安装

### 前置条件

你需要一个**免费的 Pexels API 密钥**：

1. 访问 [pexels.com/api](https://www.pexels.com/api/)
2. 注册（免费），复制你的 API Token

### QwenPaw CLI 安装（推荐）

```bash
qwenpaw plugin install pexels-search
```

### 手动安装

```bash
# 复制插件目录到 QwenPaw plugins 目录
xcopy /E /I /Y "pexels-search" "%USERPROFILE%\.qwenpaw\plugins\pexels-search"

# 安装依赖
pip install httpx
```

> ⚠️ 安装后请**重启 QwenPaw** 使插件生效。

---

## ⚙️ 配置

所有配置均通过 **QwenPaw Web UI** 完成：

1. 打开 **QwenPaw Console** → **Agent Settings** → **Tools**
2. 找到 `search_pexels_images` 和 `download_pexels_image`，点击开关启用
3. 点击每个工具旁的 ⚙️ 图标填写配置：

### `search_pexels_images`

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|:--:|--------|------|
| `pexels_token` | 密码 | ✅ | — | Pexels API 密钥（[免费获取](https://www.pexels.com/api/)） |
| `preferred_image_size` | 文本 | ❌ | `large` | AI 默认使用的图片尺寸（所有尺寸仍会并列展示） |
| `results_per_page` | 数字 | ❌ | `5` | 每次搜索返回图片数（1–80） |

### `download_pexels_image`

| 字段 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| `pexels_token` | 密码 | ✅ | 同上 |

---

## 🚀 使用示例

配置完成后，Agent 可直接调用工具。以下为实际场景示例：

### 🔎 搜索图片

> **用户:** "帮我找几张现代科技办公桌的横版图片。"

Agent 自动调用：

```
search_pexels_images(query="modern tech desk", orientation="landscape")
```

返回 5 张图片，包含所有分辨率 URL + 摄影师署名。

### 🌐 直接使用 URL

搜索结果中的 URL 可直接用于：

**HTML：**
```html
<img src="https://images.pexels.com/photos/12345/pexels-photo-12345.jpeg?w=940"
     alt="现代科技办公桌" />
```

**在线 PPT / Notion / Canva：** 粘贴 URL 到图片地址栏即可。

### 📥 下载到本地

当需要将图片嵌入本地文件（如 `python-pptx` 生成的 `.pptx`）：

> **Agent:** "下载 Pexels 图片 ID 12345。"

```
download_pexels_image(photo_id=12345)
→ 返回本地路径: C:\...\downloads\pexels-12345-large.jpg
```

---

## 🖼️ 可用图片尺寸

| Key | 分辨率 | 适用场景 |
|-----|--------|----------|
| `original` | 摄影师原始尺寸 | 打印 / 高 DPI |
| `large2x` | 940px 宽 × 2 倍高 | Retina 屏幕 |
| `large` | 940px 宽 | 网页主图 |
| `medium` | 350px 高 | 博客配图 |
| `small` | 130px 高 | 缩略图 |
| `portrait` | 800 × 1200 | 竖版布局 |
| `landscape` | 1200 × 627 | 社交分享 / OG 图 |
| `tiny` | 280 × 200 | 预览 / 网格视图 |

---

## 🎛️ 搜索参数

| 参数 | 类型 | 可选值 |
|------|------|--------|
| `query` | 字符串 | 任意搜索关键词（必填） |
| `orientation` | 字符串 | `landscape` / `portrait` / `square` |
| `size` | 字符串 | `large` / `medium` / `small` |
| `color` | 字符串 | `red` / `orange` / `yellow` / `green` / `turquoise` / `blue` / `violet` / `pink` / `brown` / `black` / `gray` / `white` |
| `locale` | 字符串 | `zh-CN` / `en-US` / `ja-JP` 等 |
| `page` | 整数 | 页码（从 1 开始） |

---

## 📁 项目结构

```
pexels-search/
├── pexels_reader.py    # 插件入口 — 工具注册
├── pexels_tools.py     # 核心逻辑 — 搜索 & 下载工具
├── plugin.json         # 插件清单（元数据、工具、配置字段）
├── requirements.txt    # Python 依赖
├── test_mock.py        # Mock 单元测试
└── README.md           # 英文文档
└── README_zh.md        # 中文文档（本文件）
```

---

## ⏱️ 速率限制

Pexels 免费额度：

- **200 次请求 / 小时**
- **20,000 次请求 / 月**

搜索结果中会显示当前剩余配额，方便把控。

---

## ❓ 常见问题

**Q: 需要注册 Pexels 账号吗？**
A: 是的，访问 [pexels.com/api](https://www.pexels.com/api/) 免费注册即可获取 API Token。

**Q: 图片可以商用吗？**
A: 可以。Pexels 图片适用于个人和商业用途，署名非强制但建议标注。详见 [Pexels License](https://www.pexels.com/license/)。

**Q: 安装后插件没有出现？**
A: 请确认已**重启 QwenPaw**。插件在启动时加载。

**Q: 报 `401 Unauthorized` 错误？**
A: Pexels API Token 无效或已过期。请在 QwenPaw Web UI → Agent Settings → Tools → search_pexels_images → ⚙️ 中重新检查并填写。

---

## 📄 许可

本插件采用 **Apache License 2.0** 开源。

通过 Pexels 获取的图片遵循 [Pexels License](https://www.pexels.com/license/) — 个人和商业用途免费，建议署名。
