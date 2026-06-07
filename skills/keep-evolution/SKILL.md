---
name: keep_evolution
description: "本技能用于优化启动文件的信息结构。触发词：'开始进化'、'重建记忆'、'优化启动文件'、'优化{某个指定的启动文件}'。当用户表达优化记忆文件意图时激活。"
version: 2.0
metadata:
  qwenpaw:
    emoji: "🧬"
    requires:
      python: ">=3.9"
---

# KEEP EVOLUTION

## 触发词

匹配以下任一触发词：

- 开始进化
- 重建记忆
- 优化启动文件
- 优化{文件名}（如"优化AGENTS.md"、"优化SOUL.md"、"优化PROFILE.md"、"优化MEMORY.md"）

## 默认读取范围

| 场景 | 读取范围 |
|------|----------|
| 默认 | AGENTS.md + SOUL.md + PROFILE.md + MEMORY.md + 当天每日记忆（memory/YYYY-MM-DD.md） |
| 当天无记忆文件 | 仅四个启动文件 |
| 用户指定文件 | 四个启动文件 + 用户指定文件/路径 |
| 用户指定近N天 | 四个启动文件 + 近N天每日记忆 |

已注入上下文的文件跳过读取。

## 五大功能模块

### 功能1：结构规范化

按写入规范调整启动文件结构。

**流程：**

1. 读取目标文件
2. 对照写入规范检查结构（见 references/ 下对应规范）
3. 检查元数据完整性（summary、read_when）
4. 调整章节顺序、格式
5. 确保符合规范

**AGENTS.md 技能工具箱自动更新：**

优化AGENTS.md时，自动扫描当前工作区，更新"常用 Skill、Tools、MCP 使用规范"章节：

1. 读取 `<workspace>/skills/` 目录，获取已安装技能列表
2. 读取 `<workspace>/agent.json`（如有），获取agent配置信息
3. 读取 `<WORKING_DIR>/config.json`，获取全局MCP配置
4. 读取各技能的 `SKILL.md` 前10行，提取触发词/用途摘要
5. 按常用度筛选，每类（Skill/Tools/MCP）最多8个
6. 按以下格式更新AGENTS.md：

```
## 常用 Skill、Tools、MCP 使用规范

**Skill：**
- skill-name（触发词/用途）
- ...（最多8个）

**Tools：**
- tool-name（用途）
- ...（最多8个）

**MCP服务：**
- mcp-name（用途，无则删除此区域）

工具并行：独立任务并行，依赖链串行。
```

**建议禁用项处理：**
- 不写入AGENTS.md
- 在进化报告末尾以"工具匹配建议"形式输出
- 列出与Agent定位不相关的skill/tool，简述原因
- 用户可自行决定是否禁用

**原则：**
- 每类最多8个，按常用度排序
- 不标注匹配度（高/中/低等）
- Tools列出Agent日常使用的内置工具
- MCP服务按需列出

**元数据格式：**

```yaml
---
summary: "文件用途简述"
read_when:
  - 手动引导工作区
  - 每次会话启动时
---
```

**各文件 summary 值：**

- AGENTS.md: "Agent工作流程、规则与指南，每次会话必读"
- SOUL.md: "Agent核心身份与行为原则"
- PROFILE.md: "用户身份信息与简历资料"
- MEMORY.md: "长期可复用经验与知识库"

---

### 功能2：信息提取

从用户指定来源提取有价值信息，写入对应文件。

**支持的来源类型：**

- 文本内容（用户直接粘贴）
- 文件路径（如 C:\xxx\README.md）
- 每日记忆（memory/YYYY-MM-DD.md）
- 对话记录

**判断写入位置的流程：**

```
内容类型？
├── Agent行为准则 → SOUL.md
├── Agent执行流程 → AGENTS.md
├── 用户偏好/习惯 → PROFILE.md
├── 实践经验/踩坑 → MEMORY.md
├── 配置/工具设置 → MEMORY.md领域知识章节
├── 专有名词 → MEMORY.md专有名词章节
└── 工作流程/SOP → MEMORY.md工作流程章节
```

**详细规则见 references/extraction-rules.md**

**写入前必须去重：**

- 完全相同：跳过
- 高度相似（>80%重叠）：合并
- 部分重叠：补充新信息
- 全新内容：新增条目

---

### 功能3：压缩减容

集成caveman技能，压缩启动文件内容。

**触发条件：**

- 默认使用 lite 模式
- 文件超过行数限制时自动切换 full 模式

**行数限制：**

| 文件 | 上限 |
|------|------|
| AGENTS.md | 60行 |
| SOUL.md | 80行 |
| PROFILE.md | 50行 |
| MEMORY.md | 150行 |

**压缩目标：**

- 删除冗余表述
- 合并重复内容
- 精简长句为短句

**调用方式：**

会话内压缩（Path A），遵循caveman技能的lite/full规则。

---

### 功能4：合规扫描

调用脚本检查启动文件合规性。

**检查项：**

- 元数据完整性（summary、read_when）
- 文件长度（是否超过上限）
- 章节完整性（必需章节是否存在）
- 格式问题（emoji、mermaid、超长代码块）
- 重复内容

**调用方式：**

```
execute_shell_command:
  command: python <skill_dir>/scripts/audit_startup_files.py <workspace_dir>
```

**输出：**

格式化报告，列出每个文件的状态（合规/有警告/不合规）及具体问题。

---

### 功能5：引导重建

发现信息不足时主动提问，帮助用户重建启动文件。

**触发条件：**

- 启动文件不存在
- 启动文件内容过少（低于合理阈值）
- 用户明确要求重建

**流程：**

1. 读取 templates/ 下对应模板
2. 向用户提问，收集必要信息
3. 按模板结构填充内容
4. 写入启动文件
5. 运行合规检查确认

**提问顺序（以PROFILE.md为例）：**

- 称呼方式
- 职业/岗位
- 核心诉求
- 技术能力边界
- 沟通偏好
- 学习风格

## 格式约束

所有写入启动文件的内容必须遵守：

- 不使用表情
- 不使用复杂长句，短句为主
- 不过多空行
- AGENTS.md / SOUL.md / PROFILE.md：不出现超过5行的代码块，不使用mermaid图、ASCII码
- MEMORY.md：代码块不超过5行（超过时拆分或简化）

## Token 估算汇报

工作流完成后，向用户汇报预估token消耗。

**估算方法：**

- 中文：约 1.5 token/字
- 英文：约 0.25 token/word

**汇报格式：**

```
本次进化预估消耗：
- 输入：X.XX k tokens
- 输出：X.XX k tokens
```

## 工作流总览

```
触发词匹配
    ↓
确定读取范围（默认4文件+当天记忆）
    ↓
读取文件
    ↓
[功能4] 运行合规扫描 → 输出报告
    ↓
[功能1] 结构规范化 → 按规范调整章节
    ↓
[功能2] 信息提取 → 从指定来源提取信息写入
    ↓
[功能3] 压缩减容 → 超限时压缩内容
    ↓
[功能5] 引导重建 → 信息不足时提问补充
    ↓
输出进化报告 + token估算
```

## 进化报告格式

```
进化报告

改动文件：{list}

具体变化：
- {file}：{what changed, why}

当前状态：
- AGENTS.md: {N} 行 (上限 60)
- SOUL.md: {N} 行 (上限 80)
- PROFILE.md: {N} 行 (上限 50)
- MEMORY.md: {N} 行 (上限 150)

本次进化预估消耗：
- 输入：X.XX k tokens
- 输出：X.XX k tokens

下次优化建议：{if any}

---
工具匹配建议（不写入文件）：
以下工具与当前Agent定位不相关，建议禁用或删除：
- {tool}（原因）
- ...
```

## 质量门控

交付报告前验证：

- 所有目标文件仍存在
- 无文件为空
- 未删除关键规则（安全、边界）
- 元数据完整
- 报告不超过20行

## 资源索引

| 文件 | 用途 |
|------|------|
| references/design-principles.md | 设计原则（读取后优化） |
| references/file-structures.md | 文件结构规范 |
| references/agents-spec.md | AGENTS.md 写入规范 |
| references/soul-spec.md | SOUL.md 写入规范 |
| references/profile-spec.md | PROFILE.md 写入规范 |
| references/memory-spec.md | MEMORY.md 写入规范 |
| references/extraction-rules.md | 信息提取与写入位置判断规则 |
| templates/ | 启动文件空白模板（含元数据） |
| scripts/audit_startup_files.py | 合规检查脚本 |
