"""
Caveman 压缩工具 — 辅助模块 v2.1
从 config.json 读取模型配置，从环境变量读取 API 密钥。
"""

import json
import os
import sys
from pathlib import Path

# skill 根目录（scripts 的上一级）
SKILL_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_ROOT / "config.json"


def load_config() -> dict:
    """
    加载 config.json 配置文件。

    返回结构:
    {
        "压缩模型": {"base_url": "...", "model_id": "..."},
        "向量比对模型": {"base_url": "...", "model_id": "..."},
        "环境变量": {"压缩模型密钥": "CAVEMAN_MODEL_KEY", "向量模型密钥": "CAVEMAN_EMBEDDING_KEY"}
    }
    """
    if not CONFIG_PATH.exists():
        print(f"错误: 配置文件不存在 {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_model_key() -> str:
    """从环境变量读取压缩模型的 API 密钥。"""
    config = load_config()
    env_name = config["环境变量"]["压缩模型密钥"]
    key = os.environ.get(env_name)
    if key:
        return key
    print(
        f"错误: 未设置环境变量 {env_name}。\n"
        f"请在 QwenPaw 设置 → 环境变量中添加：name={env_name}，Key=你的API密钥",
        file=sys.stderr,
    )
    sys.exit(1)


def get_embedding_key() -> str:
    """从环境变量读取向量比对模型的 API 密钥。"""
    config = load_config()
    env_name = config["环境变量"]["向量模型密钥"]
    key = os.environ.get(env_name)
    if key:
        return key
    print(
        f"错误: 未设置环境变量 {env_name}。\n"
        f"请在 QwenPaw 设置 → 环境变量中添加：name={env_name}，Key=你的API密钥",
        file=sys.stderr,
    )
    sys.exit(1)


def get_chat_config() -> tuple[str, str]:
    """
    获取压缩模型的 base_url 和 model_id。

    返回: (base_url, model_id)
    """
    config = load_config()
    chat = config["压缩模型"]
    return chat["base_url"], chat["model_id"]


def get_embed_config() -> tuple[str, str]:
    """
    获取向量比对模型的 base_url 和 model_id。

    返回: (base_url, model_id)
    """
    config = load_config()
    emb = config["向量比对模型"]
    return emb["base_url"], emb["model_id"]


def get_similarity_threshold() -> float:
    """
    获取相似度验证阈值，从 config.json 读取。默认 0.75。

    返回: float 阈值（0.0 ~ 1.0）
    """
    config = load_config()
    return config.get("相似度验证", {}).get("阈值", 0.75)


def get_similarity_action() -> str:
    """
    获取低于阈值时的处理策略，从 config.json 读取。默认"提醒用户"。

    返回: str 策略描述
    """
    config = load_config()
    return config.get("相似度验证", {}).get("低于阈值时", "提醒用户")
