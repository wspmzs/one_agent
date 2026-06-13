# -*- coding: utf-8 -*-
"""Pexels Image Search 插件入口。"""

import importlib.util
import logging
import os

from qwenpaw.plugins.api import PluginApi

logger = logging.getLogger(__name__)
_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_tools_module():
    """加载 pexels_tools.py。"""
    tool_path = os.path.join(_PLUGIN_DIR, "pexels_tools.py")
    spec = importlib.util.spec_from_file_location("pexels_tools", tool_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PexelsSearchPlugin:
    """Pexels Image Search Plugin。

    向 Agent 工具箱注册 search_pexels_images 和 download_pexels_image 工具。
    """

    def register(self, api: PluginApi):
        """注册工具。

        Args:
            api: PluginApi 实例。
        """
        tools = _load_tools_module()

        api.register_tool(
            tool_name="search_pexels_images",
            tool_func=tools.search_pexels_images,
            description="搜索 Pexels 高质量图片",
            icon="🔍",
        )

        api.register_tool(
            tool_name="download_pexels_image",
            tool_func=tools.download_pexels_image,
            description="下载 Pexels 图片到本地",
            icon="📥",
        )

        logger.info("pexels-search 插件已注册")


plugin = PexelsSearchPlugin()
