[![版本](https://img.shields.io/badge/version-1.0.0-blue)](./plugin.json)
[![协议](https://img.shields.io/badge/license-Apache%202.0-green)](./LICENSE)
[![QwenPaw](https://img.shields.io/badge/QwenPaw-%3E%3D1.1.6-orange)](./plugin.json)

# View Image

> Give your QwenPaw agent the ability to see.

QwenPaw agents can't natively understand images. **View Image** changes that. Connect any OpenAI-compatible VLM — a cheap multimodal model is all you need — and your agent can read screenshots, photographs, charts, UI mockups, and more.

```
describe_image(path="/path/to/screenshot.png")
```

---

## How It Works

```
 User sends an image
   → Agent calls describe_image(path)
     → Plugin encodes image (base64 or URL)
       → Sends to your VLM API
         → Returns text description
           → Agent continues with full context
```

Zero local processing. Zero hardcoded keys. All config lives in the QwenPaw Console UI.

---

## Quick Start

### 1. Install

```bash
qwenpaw plugin install /path/to/view-image
```

### 2. Configure

In QwenPaw Console → Agent Settings → Tools → **describe_image**:

| Field | Value |
|-------|-------|
| `vlm_api_url` | Your VLM endpoint, e.g. `https://ark.cn-beijing.volces.com/api/v3/chat/completions` |
| `vlm_api_key` | Your API key |
| `vlm_model_name` | Model name, e.g. `doubao-seed-2-0-lite-260428` |

### 3. Enable

Check `describe_image` in the Tools list → Save. Done.

---

## Features

- **Any VLM** — OpenAI-compatible API. Volcano Engine, OpenAI, SiliconFlow, local — all work.
- **Cheap models welcome** — Doubao lite, Qwen-VL, GPT-4o-mini.  You don't need the most expensive model.
- **Custom prompts per agent** — Designer agent focuses on layout. Data analyst focuses on trends. Each agent gets its own `prompt_template`.
- **Local + URL images** — Absolute paths and HTTP(S) URLs both supported.
- **Password-protected config** — API keys use `type: "password"` in the Console UI. Nothing in source.

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `path` | ✅ | Absolute local path or HTTP(S) URL of an image |
| `prompt` | ❌ | Custom prompt for this call (overrides `prompt_template`) |

Supported formats: png, jpg, jpeg, gif, webp, bmp.

---

## Configuration Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `vlm_api_url` | text | — | VLM API endpoint |
| `vlm_api_key` | password | — | API key (hidden in UI) |
| `vlm_model_name` | text | — | Model to call |
| `per_image_timeout` | number | 60 | Seconds per image |
| `prompt_template` | text | *(built-in)* | Default description prompt |

---

## Example: Designer Agent

Set `prompt_template` to:

> 请描述这个 UI 界面的布局结构、颜色搭配、组件类型和交互元素。用中文输出。

Then every call uses that lens.

---

## Example: Data Analyst Agent

Set `prompt_template` to:

> Describe the chart type, axis labels, data trends, outliers, and any callouts. Use English.

Each agent sees the same image differently — through its own prompt.

---

## FAQ

**The tool doesn't show up after install?** Restart QwenPaw.

**Timeout errors?** Bump `per_image_timeout` or try a smaller model.

**"VLM not configured" error?** Fill in `vlm_api_url`, `vlm_api_key`, and `vlm_model_name` in the Console UI.

---

## Dependencies

- `Pillow >= 10.0`
- `httpx >= 0.27`

---

[中文文档](README_zh.md) · Author: [impmzs](https://github.com/impmzs)
