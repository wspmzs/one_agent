# 🧬 Keep Evolution v2.0

> 优化启动文件的信息结构，让你的Agent记忆更清晰、更规范。

## ✨ 功能

| 功能 | 说明 |
|------|------|
| 📋 结构规范化 | 按模板调整启动文件的章节结构 |
| 📥 信息提取 | 从文件/文本/记忆中提取有价值信息 |
| 🗜️ 压缩减容 | 集成caveman，自动压缩超长内容 |
| 🔍 合规扫描 | 检查文件长度、结构、格式是否合规 |
| ❓ 引导重建 | 信息不足时主动提问，帮你重建文件 |

## 🚀 触发词

```
开始进化
重建记忆
优化启动文件
优化AGENTS.md（或SOUL/PROFILE/MEMORY）
```

## 📦 文件结构

```
keep-evolution/
├── SKILL.md              # 主文件（技能定义）
├── README.md             # 本文件
├── references/           # 写入规范文档
│   ├── design-principles.md
│   ├── file-structures.md
│   ├── agents-spec.md
│   ├── soul-spec.md
│   ├── profile-spec.md
│   ├── memory-spec.md
│   └── extraction-rules.md
├── templates/            # 启动文件模板（含元数据）
│   ├── AGENTS.template.md
│   ├── SOUL.template.md
│   ├── PROFILE.template.md
│   └── MEMORY.template.md
├── scripts/              # 辅助脚本
│   └── audit_startup_files.py
└── examples/             # 使用示例
```

## 📖 使用示例

### 示例1：全量优化

用户：`开始进化`

Agent行为：
1. 读取四个启动文件 + 当天每日记忆
2. 运行合规扫描，输出报告
3. 按规范调整结构
4. 压缩超长内容
5. 输出进化报告 + token估算

### 示例2：优化指定文件

用户：`优化MEMORY.md`

Agent行为：
1. 读取MEMORY.md + 当天每日记忆
2. 仅对MEMORY.md进行优化
3. 输出进化报告

### 示例3：从文件提取信息

用户：`把 C:\project\README.md 里的有用信息提取到记忆文件`

Agent行为：
1. 读取指定文件
2. 识别有价值信息（配置、经验、术语）
3. 判断写入位置
4. 去重后写入MEMORY.md

### 示例4：合规扫描

用户：`检查我的启动文件是否合规`

Agent行为：
1. 运行 audit_startup_files.py
2. 输出每个文件的状态和问题列表

## 📏 格式约束

| 约束 | 说明 |
|------|------|
| 无表情 | 启动文件不使用emoji |
| 短句 | 一.idea per line，不使用复杂长句 |
| 无mermaid | 启动文件不使用mermaid图 |
| 代码块≤5行 | AGENTS/SOUL/PROFILE不出现超过5行的代码块 |
| 元数据 | 头部必须包含summary和read_when |

## 🔧 合规检查脚本

```bash
python <skill_dir>/scripts/audit_startup_files.py <workspace_dir>
```

输出示例：
```
==================================================
启动文件合规检查报告
==================================================

【AGENTS.md】
  状态：合规
  信息：当前行数：42（上限60）

【SOUL.md】
  状态：有警告（1个）
  警告：包含超长代码块：1个

结论：共0个错误，1个警告
```

## 📊 Token估算

优化完成后，Agent会汇报预估token消耗：

```
本次进化预估消耗：
- 输入：2.50 k tokens
- 输出：1.80 k tokens
```

## 📚 参考文档

| 文档 | 用途 |
|------|------|
| design-principles.md | 设计原则 |
| file-structures.md | 文件结构规范 |
| agents-spec.md | AGENTS.md写入规范 |
| soul-spec.md | SOUL.md写入规范 |
| profile-spec.md | PROFILE.md写入规范 |
| memory-spec.md | MEMORY.md写入规范 |
| extraction-rules.md | 信息提取规则 |
