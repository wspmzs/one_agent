# -*- coding: utf-8 -*-
"""View Image Plugin entry point."""

import importlib.util
import logging
import os

from qwenpaw.plugins.api import PluginApi

logger = logging.getLogger(__name__)

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_tools_module():
    """Load image_tools.py from this plugin's directory."""
    tool_path = os.path.join(_PLUGIN_DIR, "image_tools.py")
    spec = importlib.util.spec_from_file_location("image_tools", tool_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ViewImagePlugin:
    """View Image Plugin.

    Registers describe_image tool into the Agent's toolkit.
    """

    def register(self, api: PluginApi):
        """Register describe_image tool.

        Args:
            api: PluginApi instance.
        """
        tools = _load_tools_module()

        api.register_tool(
            tool_name="describe_image",
            tool_func=tools.describe_image,
            description="Describe an image using VLM",
            icon="🖼️",
        )

        logger.info("view-image plugin registered")


# Export plugin instance
plugin = ViewImagePlugin()
