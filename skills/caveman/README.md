# 🪨 Caveman 压缩技能 — README

> **文档版本**：2.1  
> **适用 SKILL 版本**：2.1  
> **原始项目**：[JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)  
> **创建人**：张硕同学和他的 Agent 小伙伴

---

## 💡 设计理念

基于 [Caveman](https://github.com/JuliusBrussee/caveman) 压缩技术构建，摒弃纯提示词注入方案，采用双路径架构。

1. 剔除所有 LLM 可确定性重建的语法脚手架（冠词、连接词、被动语态、修饰语）。
2. 严格保留不可预测信息（数字、约束、技术术语、因果链）。
3. 支持两条使用路径：
   - **路径 A（会话内压缩）**：Agent 直接采用 caveman 风格说话。即时响应，零成本。适用于交互式对话。
   - **路径 B（外部工具压缩）**：通过 `execute_shell_command` 调用 `scripts/caveman_compress.py`。可选向量相似度校验保真度。适用于文件压缩和需要验证的场景。

---

## 🚀 快速上手

### 第 1 步：安装依赖

```bash
pip install openai numpy
```

| 依赖 | 用途 | 必装 |
|------|------|------|
| `openai` | 调用 LLM API 执行压缩（OpenAI 兼容接口） | ✅ 使用路径 B 必装 |
| `numpy` | 向量余弦相似度计算 | 仅使用 `-v` 验证时需要 |

### 第 2 步：配置 `config.json`

编辑 `skills/caveman/config.json`，填入你的 API 服务地址和模型 ID：

```json
{
  "压缩模型": {
    "base_url": "https://api.deepseek.com",
    "model_id": "deepseek-v4-flash"
  },
  "向量比对模型": {
    "base_url": "http://127.0.0.1:11434/v1",
    "model_id": "qwen3-embedding:4b"
  },
  "相似度验证": {
    "阈值": 0.75
  }
}
```

> 推荐压缩模型：DeepSeek V4 Flash，百万 tokens 输入仅 0.02 元，百万 tokens 输出仅 2 元（2026年5月计费标准）。

### 第 3 步：设置环境变量（API 密钥）

密钥不存放在文件中，必须通过环境变量配置：

| 环境变量名 | 用途 | 必填 |
|-----------|------|------|
| `CAVEMAN_MODEL_KEY` | 压缩模型的 API 密钥 | ✅ 使用路径 B 必填 |
| `CAVEMAN_EMBEDDING_KEY` | 向量比对模型的 API 密钥 | 仅使用 `-v` 验证时必填 |

**设置方法（QwenPaw 内）**：设置 → 环境变量 → 添加 → Name 填变量名，Key 填你的 API 密钥值。

> 两个模型使用同一 API 服务时，两个环境变量填相同的值即可。

### 第 4 步：验证

```bash
cd skills/caveman/scripts
python caveman_compress.py "这是一段测试文本，用来验证压缩功能是否正常工作" -i full
```

预期输出：

```
[CAVEMAN FULL]
测试文本验证压缩功能正常
```

---

## 🔌 调用方式

### 路径 A — 会话内压缩

用户说「caveman模式」「少废话」「说重点」等触发词时，Agent 直接切换说话风格，无需外部调用。

### 路径 B — 外部工具压缩

通过 `execute_shell_command` 调用：

```bash
# 压缩文本
python <skill_dir>/scripts/caveman_compress.py "待压缩文本" -i full

# 压缩文件
python <skill_dir>/scripts/caveman_compress.py -f <文件路径> -i full

# 带向量相似度验证
python <skill_dir>/scripts/caveman_compress.py -f <文件路径> -i full -v

# 输出到文件
python <skill_dir>/scripts/caveman_compress.py -f <文件路径> -i lite -o <输出路径>
```

> **注意**：QwenPaw 不支持注册自定义 Python 脚本为内置工具，始终通过 `execute_shell_command` 调用。

---

## 📐 场景路由表

| 场景 | 默认路径 | 默认强度 |
|------|---------|---------|
| 用户说「caveman模式」「少废话」 | A（会话内） | full |
| 用户说「调工具压缩」 | B（外部工具） | full |
| 用户提供文件 + 要求压缩 | B（外部工具） | full |
| 用户提供文件，未要求压缩 | 不压缩 | — |
| 用户说「lite模式」「精简模式」 | A（会话内） | lite |
| 用户说「调工具压缩，lite」 | B（外部工具） | lite |
| 用户说「通过会话LLM压缩」 | A（会话内） | full |
| 用户显式覆盖 | 按用户指定 | 按用户指定 |

---

## 🌞 预期效果

| 指标 | 效果 |
|------|------|
| Token 消耗 | 降低 30% ~ 75%（视原文冗余度与强度等级） |
| 语义保真度 | ≥ 95%（向量余弦相似度验证，阈值 0.75） |
| 逻辑链 | 零断裂（原子句拆分，禁止隐式跳跃） |
| 输出格式 | 纯净（仅压缩文本，无 Markdown 包装，无寒暄） |

---

## 📡 与「直接注入 Prompt 到上下文」对比

| 维度 | 直接注入 Prompt 到 LLM 上下文 | Python 脚本路由执行（本方案） |
|------|---------------------------|--------------------------|
| **触发条件** | 上下文 < 2000 tokens / 单次查询 / 无运行时环境 | 上下文 ≥ 2000 tokens / 需严格验证 |
| **执行速度** | 极快（单次 API 调用） | 较慢（分句调用 + 可选向量校验） |
| **保真控制** | 依赖模型遵循度，可能漂移 | 事实提取比对 + 余弦相似度阈值拦截 |
| **资源消耗** | 消耗当前 Agent 上下文窗口 | 独立进程，不占用主上下文配额 |
| **适用阶段** | 实时对话、轻量级摘要 | 关键指令下发、归档压缩、需验证场景 |

---

## 🛠️ 配置详解

### config.json 字段说明

| 字段路径 | 说明 | 示例 |
|---------|------|------|
| `压缩模型.base_url` | 执行文本压缩的 LLM API 地址 | `https://api.deepseek.com` |
| `压缩模型.model_id` | 压缩用模型 ID | `deepseek-v4-flash` |
| `向量比对模型.base_url` | Embedding API 地址 | `http://127.0.0.1:11434/v1` |
| `向量比对模型.model_id` | 向量比对模型 ID | `qwen3-embedding:4b` |
| `环境变量.压缩模型密钥` | 压缩模型密钥对应的环境变量名 | `CAVEMAN_MODEL_KEY` |
| `环境变量.向量模型密钥` | 向量模型密钥对应的环境变量名 | `CAVEMAN_EMBEDDING_KEY` |
| `相似度验证.阈值` | 相似度 PASS/WARN 分界线（0.0~1.0） | `0.75`（默认） |

> **设计原则**：base_url 和 model_id 跟 skill 走（config.json），API 密钥跟用户走（环境变量）。密钥不落盘。

---

## 📁 文件目录结构

```
skills/caveman/
├── SKILL.md                              # 核心技能定义（Agent 执行规范）
├── README.md                             # 本文档
├── config.json                           # 模型配置（base_url + model_id + 相似度阈值）
├── references/
│   └── specification.md                  # 压缩规范 v1.0（9 条核心规则）
├── scripts/
│   ├── caveman_compress.py               # CLI 压缩工具
│   └── utils.py                          # 配置加载与密钥读取
├── assets/
│   ├── setup-guide.md                    # 首次配置引导（按需读取）
│   └── prompts/
│       ├── compression_full.txt          # FULL 强度系统提示词
│       ├── compression_lite.txt          # LITE 强度系统提示词
│       └── decompression.txt             # 解压缩提示词模板
└── examples/
    └── config_example.json               # 配置示例
```

## 🔗 原始项目

https://github.com/JuliusBrussee/caveman
