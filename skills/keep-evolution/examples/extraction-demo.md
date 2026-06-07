# 信息提取示例

## 示例场景

用户说：`把这段对话里的有用信息提取到记忆文件`

用户提供的文本：
```
上次配置MCP的时候发现，npx命令在Windows上需要加.cmd后缀才能正常调用。
配置格式是这样的：
{
  "command": "npx.cmd",
  "args": ["-y", "@modelcontextprotocol/server-filesystem"]
}
另外，用户习惯在配置完成后先手动测试一下再提交，不要自动测试。
```

## Agent处理流程

### 1. 识别信息类型

分析文本内容：

| 内容 | 类型 | 写入位置 |
|------|------|----------|
| npx在Windows上需要加.cmd后缀 | 踩坑记录 | MEMORY.md |
| MCP配置格式示例 | 配置信息 | MEMORY.md领域知识章节 |
| 用户习惯先手动测试 | 用户偏好 | PROFILE.md |

### 2. 去重检查

读取MEMORY.md，检查是否已有类似内容：

- 已有"MCP配置"相关条目？→ 检查是否重复
- 已有"Windows命令"相关条目？→ 检查是否重复

### 3. 写入内容

**MEMORY.md 新增条目：**

```markdown
### Windows环境下npx命令调用（2026-05-16）

Windows上调用npx需要加.cmd后缀，否则命令找不到。

配置示例：
```json
{
  "command": "npx.cmd",
  "args": ["-y", "@modelcontextprotocol/server-filesystem"]
}
```
```

**PROFILE.md 新增偏好：**

```markdown
### 工作习惯
- **测试偏好：** 配置完成后先手动测试，再提交，不要自动测试
```

### 4. 汇报结果

```
已提取3条信息：

MEMORY.md：
- 新增：Windows环境下npx命令调用（踩坑记录+配置示例）

PROFILE.md：
- 新增：用户测试偏好

本次预估消耗：
- 输入：0.85 k tokens
- 输出：0.62 k tokens
```

## 判断逻辑说明

| 问题 | 答案 | 写入位置 |
|------|------|----------|
| 这是Agent行为准则吗？ | 否 | - |
| 这是Agent执行流程吗？ | 否 | - |
| 这是用户偏好/习惯吗？ | 是（"用户习惯先手动测试"） | PROFILE.md |
| 这是实践经验/踩坑吗？ | 是（"npx需要加.cmd后缀"） | MEMORY.md |
| 这是配置信息吗？ | 是（配置格式示例） | MEMORY.md领域知识 |
