#!/usr/bin/env python3
"""
Caveman 压缩工具 v2.1
单一调用架构，分离 chat/embedding 客户端。
从 config.json 读取模型配置，从环境变量读取 API 密钥。

用法:
    python caveman_compress.py "待压缩文本" -i full
    python caveman_compress.py -f input.txt -i lite -o output.txt
    echo "文本" | python caveman_compress.py -i full
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from utils import (
    SKILL_ROOT,
    get_chat_config,
    get_embed_config,
    get_embedding_key,
    get_model_key,
    get_similarity_threshold,
)

PROMPTS_DIR = SKILL_ROOT / "assets" / "prompts"

# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def load_prompt(filename: str) -> str:
    """加载 assets/prompts/ 下的提示词文件。"""
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"提示词文件缺失: {path}")
    return path.read_text(encoding="utf-8")


def get_chat_client():
    """创建压缩模型客户端。配置从 config.json 读取，密钥从环境变量读取。"""
    from openai import OpenAI

    base_url, _ = get_chat_config()
    api_key = get_model_key()
    return OpenAI(api_key=api_key, base_url=base_url)


def get_embed_client():
    """创建向量比对客户端。配置从 config.json 读取，密钥从环境变量读取。"""
    from openai import OpenAI

    base_url, _ = get_embed_config()
    api_key = get_embedding_key()
    return OpenAI(api_key=api_key, base_url=base_url)


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """计算两个向量的余弦相似度。"""
    a, b = np.array(v1), np.array(v2)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / norm) if norm > 0 else 0.0


# ---------------------------------------------------------------------------
# 核心逻辑
# ---------------------------------------------------------------------------


def compress_text(
    text: str,
    intensity: str = "full",
    model: str | None = None,
    calculate_embeddings: bool = False,
) -> tuple[str, float | None]:
    """
    使用配置的 LLM 压缩文本，返回 (压缩文本, 相似度)。

    参数
    ----------
    text : str
        原始输入文本。
    intensity : {"full", "lite"}
        压缩强度。
    model : str | None
        覆盖压缩模型 ID（通常不需要，config.json 已配置）。
    calculate_embeddings : bool
        为 True 时计算原文与压缩文本的余弦相似度。

    返回
    -------
    compressed : str  压缩后的文本
    similarity : float | None  余弦相似度（未开启时为 None）
    """
    client = get_chat_client()
    _, config_model = get_chat_config()
    chat_model = model or config_model

    prompt_file = (
        "compression_lite.txt" if intensity == "lite" else "compression_full.txt"
    )
    system_prompt = load_prompt(prompt_file)

    # 估算 token 数用于设置 max_tokens
    est_input_tokens = max(1, len(text) // 3)
    max_out = max(8192, int(est_input_tokens * 1.3))

    try:
        resp = client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.1,
            max_tokens=max_out,
        )
        compressed = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"压缩 API 调用失败: {e}", file=sys.stderr)
        return text, None

    similarity = None
    if calculate_embeddings:
        emb_client = get_embed_client()
        _, emb_model = get_embed_config()
        try:
            orig_emb = (
                emb_client.embeddings.create(
                    input=text, model=emb_model, encoding_format="float"
                )
                .data[0]
                .embedding
            )
            comp_emb = (
                emb_client.embeddings.create(
                    input=compressed, model=emb_model, encoding_format="float"
                )
                .data[0]
                .embedding
            )
            similarity = cosine_similarity(orig_emb, comp_emb)
        except Exception as e:
            print(f"向量验证跳过: {e}", file=sys.stderr)

    return compressed, similarity


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Caveman 压缩工具 v2.1")
    parser.add_argument("text", nargs="?", help="待压缩的文本")
    parser.add_argument("-f", "--file", help="输入文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument(
        "-i",
        "--intensity",
        default="full",
        choices=["full", "lite"],
        help="压缩强度（默认 full）",
    )
    parser.add_argument(
        "-v",
        "--validate",
        action="store_true",
        help="计算向量余弦相似度验证",
    )
    parser.add_argument("-m", "--model", help="覆盖压缩模型 ID")
    args = parser.parse_args()

    # 解析输入源
    if args.file:
        input_text = Path(args.file).read_text(encoding="utf-8").strip()
    elif args.text:
        input_text = args.text.strip()
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read().strip()
    else:
        parser.error("请提供文本、-f/--file 文件路径或管道输入")

    if not input_text:
        print("错误: 输入为空", file=sys.stderr)
        sys.exit(1)

    compressed, sim = compress_text(
        input_text,
        intensity=args.intensity,
        model=args.model,
        calculate_embeddings=args.validate,
    )

    tag = "LITE" if args.intensity == "lite" else "FULL"
    print(f"[CAVEMAN {tag}]")
    print(compressed)

    if sim is not None:
        threshold = get_similarity_threshold()
        if sim >= threshold:
            print(f"[向量相似度: {sim:.4f}] PASS (阈值: {threshold})")
        else:
            print(f"[向量相似度: {sim:.4f}] WARN (阈值: {threshold})")
            if args.intensity == "full":
                print("[建议] 相似度偏低。可尝试 lite 模式：python caveman_compress.py <输入> -i lite -v")
            else:
                print("[建议] lite 模式相似度仍偏低。建议跳过验证直接采用，或人工检查原文。")

    if args.output:
        Path(args.output).write_text(compressed, encoding="utf-8")
        print(f"已写入: {args.output}")


if __name__ == "__main__":
    main()
