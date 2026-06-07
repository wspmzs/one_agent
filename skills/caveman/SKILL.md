---
name: caveman
description: "当需要向其他智能体发送消息、需要节省 Token，或用户明确触发压缩时使用此技能。支持双路径压缩：会话内 LLM 风格（快速，无 API 成本）和外部工具（通过嵌入相似度验证）。强度级别：轻量（lite）、完整（full）。触发词：'caveman模式'、'原始人风格'、'少废话'、'tokens太多'、'说重点'、'精简模式'、'压缩本次输入'、'调工具压缩'、'通过会话LLM压缩'。"
metadata:
  qwenpaw:
    emoji: "🪨"
    version: "2.1"
    requires:
      python: ">=3.9"
      openai_sdk: ">=1.0.0"
---

# 🪨 CAVEMAN 压缩 v2.1

## 触发条件

- 「caveman模式」「原始人风格」「少废话」「tokens太多」「说重点」「精简模式」
- 「压缩本次输入」「调工具压缩」「通过会话LLM压缩」
- 任何需要提升 token 效率的对话场景

收到 `[CAVEMAN COMPRESSED]` 开头的消息时，**不再压缩**，直接使用。

## 首次使用检测

**仅当检测到以下任一情况时**，读取 `assets/setup-guide.md` 向用户展示配置引导：

- `config.json` 中 `压缩模型.base_url` 或 `压缩模型.model_id` 为空
- 环境变量 `CAVEMAN_MODEL_KEY` 未设置
- 用户首次使用路径 B 且需求模糊（未指定强度、未说明是否需要 embedding 验证）

配置完成后不重复触发。

## 压缩路径

### 路径 A — 会话内压缩

Agent 直接切换 caveman 风格。零成本，即时生效。

**规则**：丢弃冠词、填充词、客套话、模糊修饰。保留技术术语、数字、约束、否定词、因果链。代码不变。

句式：`[事物] [动作] [原因]。[下一步]。`

**退出**：「stop caveman」「normal mode」「恢复正常」。
**自动退出**：安全警告、破坏性操作确认、风险歧义、用户困惑时暂退。

### 路径 B — 外部工具压缩

`execute_shell_command` 调用 `scripts/caveman_compress.py`。

> ⚠️ **执行前确认**：Agent 必须向用户确认——① 是否需要 embedding 验证（`-v`）② 压缩强度（未指定默认 full）

**调用命令**：

```bash
# 压缩文本
python <skill_dir>/scripts/caveman_compress.py "待压缩文本" -i full
cwd: <skill_dir>/scripts

# 压缩文件
python <skill_dir>/scripts/caveman_compress.py -f <文件路径> -i full
cwd: <skill_dir>/scripts

# 带向量验证
python <skill_dir>/scripts/caveman_compress.py -f <文件路径> -i full -v
cwd: <skill_dir>/scripts

# 输出到文件（推荐）
python <skill_dir>/scripts/caveman_compress.py -f <文件路径> -i full -o <输出路径>
cwd: <skill_dir>/scripts
```

**输出格式**：

```
[CAVEMAN FULL]
压缩后的文本
[向量相似度: 0.8951] PASS (阈值: 0.75)
```

**相似度判定**（阈值在 `config.json` 的 `相似度验证.阈值` 配置，默认 0.75）：

| 相似度 | 判定 | 行为 |
|--------|------|------|
| ≥ 阈值 | PASS | 直接采用 |
| < 阈值 | WARN | full→建议降 lite 重试；lite→建议跳过验证或人工检查 |

**结果交付**：默认 `-o` 保存到文件，告知用户路径和压缩率。

## 场景路由

| 场景 | 路径 | 强度 |
|------|------|------|
| 「caveman模式」「少废话」等 | A | full |
| 「调工具压缩」 | B | full |
| 用户提供文件 + 要求压缩 | B | full |
| 用户提供文件，未要求压缩 | 不压缩 | — |
| 「lite模式」「精简模式」 | A | lite |
| 「调工具压缩，lite」 | B | lite |
| 「通过会话LLM压缩」 | A | full |

## 配置

| 位置 | 内容 |
|------|------|
| `config.json` | `压缩模型`(base_url, model_id)、`向量比对模型`(base_url, model_id)、`相似度验证`(阈值)、`环境变量`(密钥变量名) |
| 环境变量 | `CAVEMAN_MODEL_KEY`（压缩模型密钥）、`CAVEMAN_EMBEDDING_KEY`（向量模型密钥） |
| 依赖 | `pip install openai numpy` |

## 边界

- 代码/提交信息：正常风格，不压缩
- 用户文件 + 未要求压缩：不压缩
- `[CAVEMAN COMPRESSED]` 消息：不二次压缩
