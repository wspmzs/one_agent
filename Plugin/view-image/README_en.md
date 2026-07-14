[![Version](https://img.shields.io/badge/version-1.0.2-blue)](./plugin.json)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](./LICENSE)
[![QwenPaw](https://img.shields.io/badge/QwenPaw-%3C%3D2.0.0-orange)](./plugin.json)

# 🖼️ View Image

Many powerful reasoning models lack native vision capabilities — they can't understand images directly. **View Image** bridges this gap by connecting your agent to a VLM (Vision Language Model), giving it the ability to see.

Just configure an affordable multimodal model (like Doubao Lite, Qwen-VL, etc.) and your agent can read screenshots, photos, design mockups, charts, and more. With `prompt_template`, you can customize the description style per agent — a designer agent focuses on UI layout, a data analyst agent focuses on chart trends.

## ⚠️ Note

The tool name `describe_image` is deliberately different from QwenPaw's built-in `view_image` to avoid conflicts.

## 📦 Installation

Run in the terminal where QwenPaw is active:

```bash
qwenpaw plugin install /path/to/view-image
```

QwenPaw will automatically:

1. Copy the plugin to `~/.qwenpaw/plugins/`
2. Install dependencies from `requirements.txt`
3. **Hot-reload** into the running QwenPaw — no restart needed

> If QwenPaw is not running, the plugin loads on next startup.

## ⚙️ Configuration (Required)

`describe_image` **requires VLM configuration** to function — there is no fallback mode.

### Via QwenPaw Console (Recommended)

Go to QwenPaw Console → Agent Settings → Tools → `describe_image` and fill in:

| Field | Description |
|-------|-------------|
| `vlm_api_url` | VLM API endpoint (OpenAI-compatible), e.g. Volcano Engine, OpenAI, SiliconFlow |
| `vlm_api_key` | API key |
| `vlm_model_name` | Model name, e.g. `doubao-seed-2-0-lite-260428`, `qwen-vl-max` |
| `per_image_timeout` | Timeout per image in seconds (default 60) |
| `prompt_template` | Default prompt (optional, customize per agent) |

Changes take effect immediately after saving.

## ▶️ Enabling

After installation, the tool is **disabled** by default. Enable it here:

- **QwenPaw Console** → Agent Settings → Tools → Check `describe_image` → Save

## 🚀 Usage

```python
# Local image
describe_image(path="/path/to/image.jpg")

# URL image
describe_image(path="https://example.com/photo.png")

# Custom prompt (overrides the default)
describe_image(path="/path/to/image.jpg", prompt="Describe the layout and color scheme of this UI design")
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|:------:|-------------|
| `path` | str | ✅ | Absolute local path or HTTP(S) URL of the image |
| `prompt` | str | ❌ | Custom prompt for this call (overrides config default) |

### Return Value

Plain text: the image description (on success) or an error message (on failure).

## ❓ FAQ

- **VLM not configured**: Returns a clear error prompting you to configure in the Console UI.
- **VLM call timeout**: Increase `per_image_timeout` or check VLM service load.
- **Unsupported image format**: Supported formats are png, jpg, jpeg, gif, webp, bmp.

## 📦 Dependencies

- Pillow>=10.0.0
- httpx>=0.27.0

## 📄 License

This plugin is open-sourced under the **Apache License 2.0**.