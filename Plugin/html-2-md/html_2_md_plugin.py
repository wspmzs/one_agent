# -*- coding: utf-8 -*-
"""HTML转Markdown插件入口文件。"""

import logging
import os
import sys

# QwenPaw 通过 spec_from_file_location 加载入口，需先注入插件目录到 sys.path
_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
if _PLUGIN_DIR not in sys.path:
    sys.path.insert(0, _PLUGIN_DIR)

import html_2_md_tools

from qwenpaw.plugins.api import PluginApi

logger = logging.getLogger(__name__)


class Html2MdPlugin:
    """HTML转Markdown Plugin。

    向 Agent 工具箱注册 html_2_md 工具。
    """

    def register(self, api: PluginApi):
        """注册工具。"""
        api.register_tool(
            tool_name="html_2_md",
            tool_func=html_2_md_tools.html_2_md,
            description="将网页URL转换为Markdown文本",
            icon="📄",
        )
        logger.info("html-2-md 插件已注册")


plugin = Html2MdPlugin()
