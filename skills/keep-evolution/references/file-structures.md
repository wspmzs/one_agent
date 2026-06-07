# Startup File Structures

Mandatory structure for each of the four startup files. Deviate only with explicit user approval.

---

## AGENTS.md — Operating Manual

### Required Sections (in order)

```markdown
## 安全 (Safety)
- Red lines. Never-break rules.

## 内部 vs 外部 (Boundaries)
- What the agent can do freely vs must ask first.

## 技能工具箱 (Skills)
- Table of available skills with trigger descriptions.
- Skill creation workflow.

## 记忆管理 (Memory)
- What to remember, where to store it.
- Search-before-answer rule.

## 会话管理 (Session)
- Session title protocol.
- Note-taking habits.

## 沟通规范 (Communication)
- How to structure replies.
- How to explain things.
```

### Constraints
- **Max length:** 60 lines (excl. frontmatter)
- **Language:** Chinese for core instructions, English for tool names/file paths
- **Tone:** Imperative. "Do X." Not "You should do X."
- **Forbidden:** User-specific data, philosophical statements, tool implementation details

---

## SOUL.md — Identity & Voice

### Required Sections (in order)

```markdown
_Opening statement: one-line identity declaration._

## 核心准则 (Core Principles)
- Relationship definition (I'm the doer, you're the thinker)
- Communication style (no filler, direct, analytical)
- Initiative level (problem-solve first, ask for resources second)
- Translation role (you speak concepts, I speak code)

## 工作方式 (Work Style)
- Structure-first output
- Boundary awareness
- Demo over theory
- Quality gates

## 边界 (Boundaries)
- Security red lines

## 风格 (Voice)
- How to match the user's communication style
- Role-based responses (why → principles, how → execute)
```

### Constraints
- **Max length:** 80 lines
- **Language:** Chinese
- **Tone:** First-person. "I am." "I do." Not "The agent should."
- **Forbidden:** Tool names, file paths, user data, skill references

---

## PROFILE.md — User Profile

### Required Sections (in order)

```markdown
## 身份 (Identity)
- Name, role, style, principle.

## 用户资料 (User Data)
- Name, pronouns, occupation, core need.

### 技术能力边界 (Technical Constraints)
- Table: what they can/can't do.

### 沟通偏好 (Communication Preferences)
- Instruction style, reply format, explanation style, decision method.

### 学习风格 (Learning Style)
- Motivation, method, depth.

### 技术栈 (Tech Stack)
- What they understand but don't use.

### 背景 (Background)
- Strategic philosophy.
```

### Constraints
- **Max length:** 50 lines
- **Language:** Chinese
- **Tone:** Third-person descriptive. "The user is." Not "You are."
- **Forbidden:** Agent behavior rules, tool references, skill instructions

---

## MEMORY.md — Persistent Knowledge

### Required Sections (in order)

```markdown
## 工具设置 (Tool Configurations)
- Paths, commands, environment variables.
- Each entry: what + how + why it matters.

---

## 高价值经验沉淀 (High-Value Lessons)
- Trigger phrases for recovery.
- Quality gate systems.
- Configuration formats.
- Each entry: trigger word → context → solution → why it matters.
```

### Constraints
- **Max length:** 150 lines (trim when exceeds)
- **Language:** Mixed — Chinese for explanations, English for commands/paths
- **Tone:** Factual. Just the information needed to recover context.
- **Forbidden:** User preferences (goes in PROFILE.md), agent identity (goes in SOUL.md), workflow rules (goes in AGENTS.md)
