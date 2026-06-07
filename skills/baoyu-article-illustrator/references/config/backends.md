# Backend Configuration

## Architecture

baoyu-article-illustrator always generates prompts first, then dispatches to a configured backend. Switching backends only affects the image generation step — prompts stay the same.

```
Prompt files → Backend Adapter → Image files
                ├── jimeng MCP (default, built-in, zero config)
                ├── nano banana pro (external HTTP API)
                ├── GPT-image-2 (OpenAI DALL-E API)
                └── custom (any HTTP endpoint with OpenAI-compatible API)
```

## Where to Configure

### Option A: Skill config file (recommended)

Create `config/backend.yaml` in the skill directory:

```yaml
# skills/baoyu-article-illustrator/config/backend.yaml
active: jimeng            # jimeng | nano-banana-pro | gpt-image-2 | custom

jimeng:
  default_model: doubao-seedream-5-0-260128
  fallback_chain:
    - doubao-seedream-5-0-lite-260128
    - doubao-seedream-4-5-251128

nano-banana-pro:
  api_url: "https://api.nano-banana.com/v1/images/generations"
  api_key_env: "NANO_BANANA_API_KEY"      # read from env var
  default_model: nano-banana-pro-v1
  timeout: 120

gpt-image-2:
  api_url: "https://api.openai.com/v1/images/generations"
  api_key_env: "OPENAI_API_KEY"
  default_model: dall-e-3
  default_size: "1792x1024"
  timeout: 120

custom:
  api_url: "https://your-api.example.com/v1/generate"
  api_key_env: "CUSTOM_IMAGE_API_KEY"
  default_model: your-model-name
  timeout: 120
```

### Option B: Memory / PROFILE.md

For per-user backend preference:

```yaml
# In MEMORY.md or project config
baoyu-article-illustrator:
  backend:
    active: jimeng
    # API keys NOT stored here — always use environment variables
```

### API Keys — Environment Variables Only

API keys must be set as environment variables, never hardcoded in config files:

**Windows:**
```powershell
$env:NANO_BANANA_API_KEY = "your-key"
$env:OPENAI_API_KEY = "your-key"
```

**Linux/Mac:**
```bash
export NANO_BANANA_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

For qwenpaw, set these before starting the agent, or add to system environment variables.

## Backend Details

### jimeng MCP (Default)

| Field | Value |
|-------|-------|
| Type | Built-in MCP tool |
| Auth | Automatic (qwenpaw account) |
| Config needed | None |
| Models | `list_models()` at runtime |
| Aspect ratios | `list_sizes(model)` at runtime |
| Limitations | 24h URL expiry, no stream mode |
| Reference images | `generate_image_with_reference` |

**Zero-config. Always works if qwenpaw is running.**

### nano banana pro

| Field | Value |
|-------|-------|
| Type | External HTTP API |
| Auth | API key in `NANO_BANANA_API_KEY` env var |
| Config needed | `api_url`, `api_key_env`, `default_model` |
| API format | OpenAI-compatible `/v1/images/generations` |
| Invocation | `execute_shell_command` with `curl` or Python `requests` |

**Call pattern:**
```python
import os, requests

resp = requests.post(
    os.environ["NANO_BANANA_API_KEY"],
    json={
        "model": "nano-banana-pro-v1",
        "prompt": prompt_text,
        "n": 1,
        "size": "16:9"
    },
    headers={"Authorization": f"Bearer {os.environ['NANO_BANANA_API_KEY']}"},
    timeout=120
)
image_url = resp.json()["data"][0]["url"]
```

### GPT-image-2 (DALL-E)

| Field | Value |
|-------|-------|
| Type | OpenAI API |
| Auth | API key in `OPENAI_API_KEY` env var |
| Config needed | `api_url`, `api_key_env`, `default_model` |
| API format | Standard OpenAI Images API |
| Sizes | `1024x1024`, `1792x1024`, `1024x1792` |

**Call pattern:**
```python
import os, requests

resp = requests.post(
    "https://api.openai.com/v1/images/generations",
    json={
        "model": "dall-e-3",
        "prompt": prompt_text,
        "n": 1,
        "size": "1792x1024",
        "quality": "hd"
    },
    headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
    timeout=120
)
image_url = resp.json()["data"][0]["url"]
```

### Custom Backend

Any OpenAI-compatible image generation endpoint. Configure:

| Field | Required | Description |
|-------|----------|-------------|
| `api_url` | Yes | Full endpoint URL |
| `api_key_env` | Yes | Environment variable name for API key |
| `default_model` | Yes | Model name to pass in request body |
| `timeout` | No | Request timeout in seconds (default: 120) |

## Switching Backends

### At setup time (first use)
Agent asks: "Which image generation backend?"

| Option | Config needed |
|--------|--------------|
| jimeng (built-in) | None |
| nano banana pro | API key in env var |
| GPT-image-2 (DALL-E) | API key in env var |
| Custom | API URL + API key in env var |

### At runtime
Edit `config/backend.yaml` → `active: [name]`. Restart not required — skill reads config each invocation.

### Override per article
User says: "use GPT-image-2 for this article" → agent uses that backend for this session only, without changing default config.
