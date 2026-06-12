# -*- coding: utf-8 -*-
"""View Image tool implementation.

Analyzes a single image using VLM model.
Supports local file path or HTTP(S) URL.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse
from qwenpaw.plugins import get_tool_config

# Ensure this plugin's directory is in sys.path for sibling imports
_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
if _PLUGIN_DIR not in sys.path:
    sys.path.insert(0, _PLUGIN_DIR)

import vlm_client

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}


def _is_url(path: str) -> bool:
    """Check if the path is an HTTP(S) URL."""
    return path.lower().startswith(("http://", "https://"))


def _validate_path(path: str) -> str | None:
    """Validate the image path.

    Args:
        path: Local file path or URL.

    Returns:
        Error message string if invalid, None if valid.
    """
    if not path or not path.strip():
        return "图片路径不能为空"

    if _is_url(path):
        return None  # URL validation is done by VLM API

    p = Path(path)
    if not p.exists():
        return f"文件不存在: {path}"

    ext = p.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return (
            f"不支持的图片格式 '{ext}'，"
            f"支持: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    return None


def _get_vlm_config() -> dict | None:
    """Read VLM configuration from tool config.

    Returns:
        Dict with 'api_url', 'api_key', 'model_name', 'timeout',
        'prompt' keys, or None if not configured.
    """
    config = get_tool_config("describe_image")
    if not config:
        return None

    api_url = (config.get("vlm_api_url") or "").strip()
    api_key = (config.get("vlm_api_key") or "").strip()
    model_name = (config.get("vlm_model_name") or "").strip()

    if not api_url or not api_key or not model_name:
        return None

    timeout = config.get("per_image_timeout")
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        timeout = 60

    prompt = (config.get("prompt_template") or "").strip()

    return {
        "api_url": api_url,
        "api_key": api_key,
        "model_name": model_name,
        "timeout": int(timeout),
        "prompt": prompt or None,
    }


async def describe_image(
    path: str,
    prompt: str = None,
) -> ToolResponse:
    """Analyze a single image using VLM model.

    Args:
        path (str):
            Local file absolute path or HTTP(S) URL of the image.
            Only single image per call (required).
        prompt (str, optional):
            Custom prompt for this image analysis.
            Overrides the config_fields prompt_template for this call.
            Defaults to the prompt_template in config.

    Returns:
        ToolResponse:
            Contains the image description text.

    Note:
        - This tool requires VLM configuration to be set.
        - For multiple images, call this tool multiple times.
        - Tool name 'describe_image' avoids conflict with built-in
          'view_image' tool.
    """
    try:
        # Validate path
        err_msg = _validate_path(path)
        if err_msg:
            return ToolResponse(
                content=[TextBlock(type="text", text=f"Error: {err_msg}")]
            )

        # Read VLM config
        vlm_config = _get_vlm_config()
        if not vlm_config:
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=(
                            "Error: describe_image 需要配置 VLM。"
                            "请在 QwenPaw Console → Agent Settings → Tools "
                            "→ describe_image 中填写 api_url、api_key、"
                            "model_name。"
                        ),
                    )
                ]
            )

        # Determine prompt: parameter overrides config default
        effective_prompt = prompt or vlm_config["prompt"]

        # Call VLM
        description = await vlm_client.describe_image(
            image_path=path,
            api_url=vlm_config["api_url"],
            api_key=vlm_config["api_key"],
            model_name=vlm_config["model_name"],
            prompt=effective_prompt,
            timeout=vlm_config["timeout"],
        )

        # Check for error placeholder
        if description.startswith("[图片:"):
            return ToolResponse(
                content=[TextBlock(type="text", text=f"Error: {description}")]
            )

        source_label = path if len(path) <= 80 else f"...{path[-77:]}"
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=(
                        f"## 图片分析结果\n\n"
                        f"**图片来源**: {source_label}\n\n"
                        f"{description}"
                    ),
                )
            ]
        )

    except asyncio.TimeoutError:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text="Error: VLM 调用超时，请检查网络或增大 per_image_timeout",
                )
            ]
        )
    except Exception as e:
        logger.exception("describe_image failed")
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"Error: 图片分析失败 - {str(e)}",
                )
            ]
        )
