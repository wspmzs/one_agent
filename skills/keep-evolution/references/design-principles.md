# Design Principles for Startup Files

Derived from Anthropic official best practices, community CLAUDE.md patterns, and real usage experience.

## Core Principles

### 1. Entry File = Workflow, Not Encyclopedia

AGENTS.md is the first thing loaded. It should define **how to operate**, not dump all knowledge. Target: ~50 lines max for the main workflow file. Move detail to referenced files.

**Source:** dev.to article — "Keep CLAUDE.md around 30 lines... use it as an entry point that defines the workflow. The LLM then decides which docs to read."

### 2. Living Document, Not One-Time Config

Every correction, every "you got this wrong" → becomes a rule. Every new discovery → gets documented. The files evolve through daily use.

**Source:** Anthropic — "When Claude makes a wrong assumption, tell it to add the correction to CLAUDE.md." Tencent Cloud — "Organic construction through daily work."

### 3. Sacrifice Grammar for Conciseness

Caveman talk. Short sentences. One idea per line. Remove filler words. The model reads faster, wastes fewer tokens, stays more focused.

**Source:** dev.to — "Be extremely concise. Sacrifice grammar for the sake of conciseness."

### 4. Separation of Concerns

| File | Role | What Goes Here |
|------|------|----------------|
| AGENTS.md | Operating manual | Rules, tools, workflows, how to act |
| SOUL.md | Identity & style | Who I am, how I think, how I talk |
| PROFILE.md | User data | Who the user is, their constraints, preferences |
| MEMORY.md | Persistent knowledge | Configs, trigger phrases, lessons learned |

Each file has ONE job. No overlap. If a rule belongs in two places, it's in the wrong place.

### 5. Conflict Resolution Protocol

When information conflicts:

1. **User's recent explicit preference** (from current or most recent session) — highest priority
2. **Documented rule in the correct file** (e.g., style rule in SOUL.md)
3. **Community best practice** (from reference articles)
4. **Default model behavior** — lowest priority

When unsure, ASK the user: "Found conflict between X and Y. Which wins?"

### 6. Staleness Protocol (>5 Days No Update)

If a file hasn't been modified in 5+ days:

1. Read the file
2. Check if any rules/entries are:
   - **Obsolete** — project changed, tool changed → remove
   - **Redundant** — same info in two places → merge, keep one
   - **Never triggered** — memory entry never referenced → trim or archive to `memory/YYYY-MM-DD-archived.md`
   - **Still valid** → leave as-is
3. Ask user: "These entries are >5 days old. Still relevant? [list]"
4. Trim confirmed obsolete items

### 7. Length & Structure Optimization

**AGENTS.md:**
- Target: 30-60 lines
- Structure: Safety → Boundaries → Skills → Memory → Session → Communication
- Every rule must be actionable. If it's philosophy, put it in SOUL.md.

**SOUL.md:**
- Target: 40-80 lines
- Structure: Identity → Principles → Work style → Boundaries → Voice
- No tool references. No user data. Pure identity.

**PROFILE.md:**
- Target: 30-50 lines
- Structure: Identity → User profile → Constraints → Preferences → Background
- Every entry answers "What should the agent know before talking to this person?"

**MEMORY.md:**
- Target: 50-100 lines (grows over time, gets trimmed periodically)
- Structure: Tool configs → Trigger phrases → Lessons learned
- Each entry should have a "why it matters" — not just what happened, but why it matters for future sessions.

### 8. When to Add vs. When to Trim

**ADD when:**
- User corrects agent behavior → becomes a rule
- New tool/process discovered → becomes a memory entry
- User expresses a preference → goes to PROFILE.md
- Agent realizes how to do something better → becomes a principle in SOUL.md

**TRIM when:**
- Two entries say the same thing → merge
- Entry hasn't been referenced in 5+ sessions → archive
- Entry is implementation detail, not principle → remove (it should be in a Skill or daily note)
- Entry uses 3 sentences where 1 works → condense

### 9. 规则必须附原因（Reason-Anchored Rule）

在AGENTS.md/SOUL.md/PROFILE.md/MEMORY.md中写入规则时，不能只写"能做什么/禁止做什么"，必须用简单语言在规则后面附上原因。

**格式规范：**
- 禁令格式：「禁止xxx，因为xxxx。如果禁令可能导致xx，最严重的后果是xxxx。」
- 许可格式：「你可以xxx，因为xxxx。」
- 如果有多个原因，只写最重要的一个。
- 如果有多个后果，只写最严重的一个。
- 原因要用简单语言，避免术语堆砌。

**原因：** 行为示范只能覆盖已知场景。没有原因支撑的规则，Agent在遇到规则未覆盖的极端情况时，会自行推理出偏离预期的结论（如"自保比服从更重要"）。附上原因能让Agent理解规则背后的价值观，在没有明确指令时也能做出正确判断。
