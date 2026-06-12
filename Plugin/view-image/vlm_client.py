# -*- coding: utf-8 -*-
"""VLM API client for image description.

Provides async function to call any OpenAI-compatible VLM API.
Supports base64-encoded local images and URL images.
"""

import base64
import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# Default prompt used when config does not provide one
DEFAULT_PROMPT = (
    "请用中文简要描述这张图片的内容。"
    "如果图片包含文字，请提取文字内容。"
    "如果图片是图表或数据可视化，请描述图表类型和数据趋势。"
)


def _encode_image(image_path: str) -> str:
    """Encode a local image file to base64 data URI.

    Args:
        image_path: Path to the local image file.

    Returns:
        Base64 data URI string (data:image/xxx;base64,...).
    """
    path = Path(image_path)
    ext = path.suffix.lower().lstrip(".")
    mime_map = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
        "bmp": "image/bmp",
    }
    mime = mime_map.get(ext, "image/png")
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _is_url(path: str) -> bool:
    """Check if the path is an HTTP(S) URL."""
    return path.lower().startswith(("http://", "https://"))


def _build_messages(image_path: str, prompt: str) -> list:
    """Build the messages array for the VLM API call.

    Args:
        image_path: Local file path or URL.
        prompt: Text prompt to send with the image.

    Returns:
        List of message dicts for the API request body.
    """
    if _is_url(image_path):
        image_content = {
            "type": "image_url",
            "image_url": {"url": image_path},
        }
    else:
        data_uri = _encode_image(image_path)
        image_content = {
            "type": "image_url",
            "image_url": {"url": data_uri},
        }

    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                image_content,
            ],
        }
    ]


async def describe_image(
    image_path: str,
    api_url: str,
    api_key: str,
    model_name: str,
    prompt: str | None = None,
    timeout: int = 60,
) -> str:
    """Describe an image using a VLM API (OpenAI-compatible).

    Args:
        image_path: Local file path or HTTP(S) URL of the image.
        api_url: VLM API endpoint URL.
        api_key: API key for authentication.
        model_name: Model name to use.
        prompt: Custom prompt. Falls back to DEFAULT_PROMPT if None.
        timeout: Per-image timeout in seconds (default 60).

    Returns:
        Image description text. On failure, returns a descriptive
        error string starting with ``[图片: ...]``.
    """
    if not prompt:
        prompt = DEFAULT_PROMPT

    messages = _build_messages(image_path, prompt)

    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
            response = await client.post(
                api_url, json=payload, headers=headers
            )
            response.raise_for_status()
            data = response.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            if not content:
                return "[图片: VLM 返回内容为空]"
            return content.strip()

    except httpx.TimeoutException:
        return f"[图片: 分析超时（{timeout}s）]"
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text[:200] if exc.response.text else ""
        return f"[图片: VLM 调用失败 (HTTP {status}) - {detail}]"
    except httpx.RequestError as exc:
        return f"[图片: VLM 请求失败 - {exc}]"
    except Exception as exc:
        logger.exception("Unexpected VLM error for %s", image_path)
        return f"[图片: 分析失败 - {exc}]"
