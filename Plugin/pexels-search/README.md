# 🔍 Pexels Search — QwenPaw Plugin

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](./plugin.json)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![QwenPaw](https://img.shields.io/badge/QwenPaw-%3E%3D1.1.6-orange)](./plugin.json)

QwenPaw plugin for Pexels image search🔍. Natural-language queries with orientation, size, color, and locale filters. 8 resolution variants, local download support. Secure token config via Web UI — no credentials in code. 200 req/hr free tier. Perfect for Agent-driven PPT, front-end, and content generation workflows.

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🚀 Usage](#-usage)
- [🖼️ Available Image Sizes](#️-available-image-sizes)
- [🎛️ Search Parameters](#️-search-parameters)
- [📁 Project Structure](#-project-structure)
- [⏱️ Rate Limits](#️-rate-limits)
- [❓ FAQ](#-faq)
- [📄 License](#-license)

---

## ✨ Features

- **🔎 Smart Search** — Natural-language queries with orientation, size, color, and locale filters
- **📥 Local Download** — Download any image directly to your machine for offline use
- **🎨 Multiple Sizes** — 8 resolution variants from `tiny` thumbnail to `original` quality
- **📊 Rich Metadata** — Photographer name, dimensions, dominant color, and attribution URL per image
- **🔐 Secure Config** — API token managed through QwenPaw Web UI, never exposed in code
- **📉 Rate-Limit Aware** — Displays remaining quota so you never hit the wall unexpectedly

---

## 📦 Installation

### Prerequisites

Before installing, you'll need a **free Pexels API key**:

1. Go to [pexels.com/api](https://www.pexels.com/api/)
2. Sign up (free) and copy your API token

### Via QwenPaw CLI (recommended)

```bash
qwenpaw plugin install pexels-search
```

### Manual Install

```bash
# Copy the plugin folder into your QwenPaw plugins directory
xcopy /E /I /Y "pexels-search" "%USERPROFILE%\.qwenpaw\plugins\pexels-search"

# Install dependencies
pip install httpx
```

> ⚠️ **Restart QwenPaw** after installation for the plugin to take effect.

---

## ⚙️ Configuration

All configuration is done in the **QwenPaw Web UI**:

1. Open **QwenPaw Console** → **Agent Settings** → **Tools**
2. Locate `search_pexels_images` and `download_pexels_image`, then toggle them **on**
3. Click the ⚙️ icon next to each tool and fill in:

### `search_pexels_images`

| Field | Type | Required | Default | Description |
|-------|------|:--------:|---------|-------------|
| `pexels_token` | password | ✅ | — | Your Pexels API key ([get one free](https://www.pexels.com/api/)) |
| `preferred_image_size` | text | ❌ | `large` | Default size the AI uses (all sizes are still listed) |
| `results_per_page` | number | ❌ | `5` | Images per search (1–80) |

### `download_pexels_image`

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `pexels_token` | password | ✅ | Same token as above |

---

## 🚀 Usage

Once configured, your Agent can invoke the tools directly. Here are some real-world scenarios:

### 🔎 Search Images

> **User:** "Find me some modern tech desk setups in landscape orientation."

The Agent will automatically call:

```
search_pexels_images(query="modern tech desk", orientation="landscape")
```

And return 5 images with all resolution URLs + photographer credits.

### 🌐 Use URLs Directly

After getting search results, the Agent can embed URLs in:

**HTML:**
```html
<img src="https://images.pexels.com/photos/12345/pexels-photo-12345.jpeg?w=940"
     alt="Modern tech desk workspace" />
```

**Online PPT / Notion / Canva:** Paste the URL into the image address bar.

### 📥 Download to Local

When you need the actual file (e.g., embedding in a `.pptx` via `python-pptx`):

> **Agent:** "Download Pexels image ID 12345."

```
download_pexels_image(photo_id=12345)
→ Returns: C:\...\downloads\pexels-12345-large.jpg
```

---

## 🖼️ Available Image Sizes

| Key | Resolution | Use Case |
|-----|------------|----------|
| `original` | Photographer's original | Print / high-DPI |
| `large2x` | 940px × 2× height | Retina screens |
| `large` | 940px wide | Web hero images |
| `medium` | 350px tall | Blog posts |
| `small` | 130px tall | Thumbnails |
| `portrait` | 800 × 1200 | Vertical layouts |
| `landscape` | 1200 × 627 | Social media / OG images |
| `tiny` | 280 × 200 | Previews / grids |

---

## 🎛️ Search Parameters

| Parameter | Type | Values |
|-----------|------|--------|
| `query` | string | Any search term (required) |
| `orientation` | string | `landscape` / `portrait` / `square` |
| `size` | string | `large` / `medium` / `small` |
| `color` | string | `red` / `orange` / `yellow` / `green` / `turquoise` / `blue` / `violet` / `pink` / `brown` / `black` / `gray` / `white` |
| `locale` | string | `zh-CN` / `en-US` / `ja-JP` / etc. |
| `page` | integer | Page number (starts at 1) |

---

## 📁 Project Structure

```
pexels-search/
├── pexels_reader.py    # Plugin entry point — tool registration
├── pexels_tools.py     # Core logic — search & download tools
├── plugin.json         # Plugin manifest (metadata, tools, config fields)
├── requirements.txt    # Python dependencies
├── test_mock.py        # Unit tests with mocked HTTP responses
└── README.md           # This file
```

---

## ⏱️ Rate Limits

Pexels free tier provides:

- **200 requests / hour**
- **20,000 requests / month**

Search results include your current remaining quota so you always know where you stand.

---

## ❓ FAQ

**Q: Do I need a Pexels account?**
A: Yes — register for free at [pexels.com/api](https://www.pexels.com/api/) to get an API token.

**Q: Can I use the images commercially?**
A: Yes. Pexels images are licensed for both personal and commercial use. Attribution to the photographer is appreciated but not required. See the [Pexels License](https://www.pexels.com/license/).

**Q: The plugin doesn't appear after installation.**
A: Make sure you've **restarted QwenPaw**. Plugins are loaded at startup.

**Q: I get a `401 Unauthorized` error.**
A: Your Pexels API token is invalid or expired. Double-check it in the QwenPaw Web UI under Agent Settings → Tools → search_pexels_images → ⚙️.

---

## 📄 License

This plugin is open-sourced under the **Apache License 2.0**.

Images retrieved via Pexels are governed by the [Pexels License](https://www.pexels.com/license/) — free for personal and commercial use, attribution appreciated.
