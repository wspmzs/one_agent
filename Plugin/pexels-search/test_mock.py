# -*- coding: utf-8 -*-
"""pexels-search mock 测试。

验证 Tool 函数在「无 Token」和「正常配置」两种路径下的行为。
"""

import sys
import os
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

# 将项目目录加入 sys.path，以便 import pexels_tools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---- Mock QwenPaw 依赖 ----
class TextBlock(dict):
    def __init__(self, type="text", text=""):
        super().__init__()
        self["type"] = type
        self["text"] = text

class ToolResponse:
    def __init__(self, content=None):
        self.content = content or []

# 构造能正常 import 的假模块
class FakeModule:
    """模拟 Python 模块，from X import Y 时 Y 通过 __dict__ 查找。"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

_agentscope_message = FakeModule(TextBlock=TextBlock)
_agentscope_tool = FakeModule(ToolResponse=ToolResponse)
_qwenpaw_plugins = FakeModule(get_tool_config=MagicMock())

sys.modules["qwenpaw"] = FakeModule()
sys.modules["qwenpaw.plugins"] = _qwenpaw_plugins
sys.modules["agentscope"] = FakeModule()
sys.modules["agentscope.message"] = _agentscope_message
sys.modules["agentscope.tool"] = _agentscope_tool

import pexels_tools

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name}  {detail}")


def _make_client_mock(*mock_resps):
    """构造 httpx.AsyncClient 的 mock，get() 返回 mock_resps。
    
    mock_resps 是 MagicMock 序列，每个代表一次 HTTP 响应。
    """
    get_mock = AsyncMock(side_effect=mock_resps)
    client = MagicMock()
    client.__aenter__ = AsyncMock()
    client.__aenter__.return_value.get = get_mock
    client.__aexit__ = AsyncMock(return_value=None)
    return client


# ============================================================
# 测试 1: search — 无 Token 返回错误
# ============================================================
async def test_search_no_token():
    print("\n=== Test 1: search 无 Token ===")
    with patch("pexels_tools.get_tool_config", return_value={}):
        result = await pexels_tools.search_pexels_images(query="nature")
    text = result.content[0]["text"]
    check("返回 ToolResponse", isinstance(result, ToolResponse))
    check("包含 Error", "Error" in text, detail=text[:100])
    check("提示配置 Token", "pexels_token" in text, detail=text[:100])


# ============================================================
# 测试 2: search — 空 query 参数
# ============================================================
async def test_search_empty_query():
    print("\n=== Test 2: search 空 query ===")
    cfg = {"pexels_token": "fake-token", "results_per_page": 3,
           "preferred_image_size": "large"}
    with patch("pexels_tools.get_tool_config", return_value=cfg):
        result = await pexels_tools.search_pexels_images(query="")
    text = result.content[0]["text"]
    check("返回 Error", "Error" in text)
    check("提示 query 不能为空", "query" in text.lower())


# ============================================================
# 测试 3: search — 正常路径
# ============================================================
async def test_search_success():
    print("\n=== Test 3: search 正常路径 ===")
    cfg = {"pexels_token": "fake-token", "results_per_page": 3,
           "preferred_image_size": "large"}
    mock_photos = [
        {"id": 1, "alt": "Sunset over mountains",
         "photographer": "张测试", "photographer_url": "https://pexels.com/@test",
         "width": 1920, "height": 1080, "avg_color": "#7E5835",
         "url": "https://pexels.com/photo/1/",
         "src": {"original": "https://.../1/original.jpg",
                 "large": "https://.../1/large.jpg",
                 "medium": "https://.../1/medium.jpg",
                 "small": "https://.../1/small.jpg"}},
        {"id": 2, "alt": "Ocean waves",
         "photographer": "李海洋", "photographer_url": "https://pexels.com/@ocean",
         "width": 2560, "height": 1440, "avg_color": "#1E90FF",
         "url": "https://pexels.com/photo/2/",
         "src": {"original": "https://.../2/original.jpg",
                 "large": "https://.../2/large.jpg",
                 "tiny": "https://.../2/tiny.jpg"}},
    ]

    resp = MagicMock()
    resp.status_code = 200
    resp.headers = {"X-Ratelimit-Limit": "200",
                    "X-Ratelimit-Remaining": "198"}
    resp.json = MagicMock(return_value={
        "total_results": 10, "page": 1, "photos": mock_photos})
    client = _make_client_mock(resp)

    with patch("pexels_tools.get_tool_config", return_value=cfg), \
         patch("pexels_tools.httpx.AsyncClient", return_value=client):
        result = await pexels_tools.search_pexels_images(query="nature")
    text = result.content[0]["text"]
    check("ToolResponse", isinstance(result, ToolResponse))
    check("搜索词", "nature" in text)
    check("图片1 alt", "Sunset over mountains" in text)
    check("图片2 alt", "Ocean waves" in text)
    check("摄影师", "张测试" in text and "李海洋" in text)
    check("署名提示", "Pexels" in text and "免费使用" in text)
    check("速率限制", "198" in text)
    check("默认推荐标记", "默认推荐" in text)
    check("多尺寸展示", "original" in text and "medium" in text and "small" in text)


# ============================================================
# 测试 4: search — 无结果
# ============================================================
async def test_search_no_results():
    print("\n=== Test 4: search 无结果 ===")
    cfg = {"pexels_token": "fake-token", "results_per_page": 5,
           "preferred_image_size": "large"}
    resp = MagicMock()
    resp.status_code = 200
    resp.headers = {}
    resp.json = MagicMock(return_value={"total_results": 0, "page": 1,
                                        "photos": []})
    client = _make_client_mock(resp)

    with patch("pexels_tools.get_tool_config", return_value=cfg), \
         patch("pexels_tools.httpx.AsyncClient", return_value=client):
        result = await pexels_tools.search_pexels_images(query="xyzzyx")
    text = result.content[0]["text"]
    check("ToolResponse", isinstance(result, ToolResponse))
    check("提示无结果", "无结果" in text)


# ============================================================
# 测试 5: search — Token 无效 (401)
# ============================================================
async def test_search_401():
    print("\n=== Test 5: search Token 无效 (401) ===")
    cfg = {"pexels_token": "bad-token", "results_per_page": 5,
           "preferred_image_size": "large"}
    resp = MagicMock()
    resp.status_code = 401
    resp.text = "Unauthorized"
    client = _make_client_mock(resp)

    with patch("pexels_tools.get_tool_config", return_value=cfg), \
         patch("pexels_tools.httpx.AsyncClient", return_value=client):
        result = await pexels_tools.search_pexels_images(query="test")
    text = result.content[0]["text"]
    check("401 错误", "401" in text and "Token 无效" in text)


# ============================================================
# 测试 6: download — 无 Token 返回错误
# ============================================================
async def test_download_no_token():
    print("\n=== Test 6: download 无 Token ===")
    with patch("pexels_tools.get_tool_config", return_value={}):
        result = await pexels_tools.download_pexels_image(photo_id=12345)
    text = result.content[0]["text"]
    check("ToolResponse", isinstance(result, ToolResponse))
    check("Error", "Error" in text)
    check("提示配置 Token", "pexels_token" in text)


# ============================================================
# 测试 7: download — 无效 photo_id
# ============================================================
async def test_download_bad_id():
    print("\n=== Test 7: download 无效 photo_id ===")
    cfg = {"pexels_token": "fake-token"}
    with patch("pexels_tools.get_tool_config", return_value=cfg):
        result = await pexels_tools.download_pexels_image(photo_id=0)
    text = result.content[0]["text"]
    check("Error", "Error" in text)
    check("photo_id 无效", "photo_id" in text.lower())


# ============================================================
# 测试 8: download — 正常路径
# ============================================================
async def test_download_success():
    print("\n=== Test 8: download 正常路径 ===")
    cfg = {"pexels_token": "fake-token"}
    mock_photo = {
        "id": 12345, "alt": "Mountain sunset",
        "photographer": "王山峰", "photographer_url": "https://pexels.com/@mountain",
        "width": 4000, "height": 3000, "avg_color": "#FF4500",
        "url": "https://pexels.com/photo/12345/",
        "src": {"original": "https://.../12345/original.jpg",
                "large": "https://.../12345/large.jpg",
                "medium": "https://.../12345/medium.jpg"},
    }

    meta_resp = MagicMock()
    meta_resp.status_code = 200
    meta_resp.json = MagicMock(return_value=mock_photo)

    dl_resp = MagicMock()
    dl_resp.status_code = 200
    dl_resp.content = b"\xff\xd8\xff\xe0" * 1000

    client = _make_client_mock(meta_resp, dl_resp)

    with patch("pexels_tools.get_tool_config", return_value=cfg), \
         patch("pexels_tools.httpx.AsyncClient", return_value=client), \
         patch("builtins.open", MagicMock()):
        result = await pexels_tools.download_pexels_image(
            photo_id=12345, output_dir="/tmp/test", size="large")

    text = result.content[0]["text"]
    check("ToolResponse", isinstance(result, ToolResponse))
    check("文件路径", "文件路径" in text)
    check("摄影师", "王山峰" in text)
    check("署名 HTML", "Pexels" in text and "Photo</a>" in text)
    check("图片描述", "Mountain sunset" in text)


# ============================================================
# 主入口
# ============================================================
async def main():
    global passed, failed
    print("=" * 60)
    print("pexels-search Mock 测试")
    print("=" * 60)

    await test_search_no_token()
    await test_search_empty_query()
    await test_search_success()
    await test_search_no_results()
    await test_search_401()
    await test_download_no_token()
    await test_download_bad_id()
    await test_download_success()

    print("\n" + "=" * 60)
    total = passed + failed
    print(f"结果: {passed}/{total} 通过", end="")
    if failed > 0:
        print(f", {failed} 失败")
    else:
        print(" [OK] 全部通过!")
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
