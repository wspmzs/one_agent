---
name: skill_creator
description: "This skill should be used when the user asks to 'create a skill', 'write a new skill', 'add a skill', 'make a skill', 'improve a skill', 'fix the skill', 'how to make a skill', 'skill template', 'what is a skill', or needs guidance on creating, editing, or validating QwenPaw skills."
metadata:
  qwenpaw:
    emoji: "✏️"
    requires: {}
---

# SKILL CREATOR

## RULES (must follow)

**Description** (frontmatter, YAML):
- Third person only. Start with: `"This skill should be used when..."`
- Add trigger phrases in quotes. 5 minimum. Real things user says.
- Example: `"…asks to 'create a skill', 'write a skill', 'add a skill'…"`

**Body** (everything under `---`):
- Imperative form only. No "you should". No "you need".
- ✅ `To create a skill, define the name.`
- ❌ `You should define the name.`
- Direct. Short sentences. One idea per line.

## SKILL ANATOMY

```
skills/skill-name/
├── SKILL.md           ← Required. The skill.
├── references/        ← Big docs. Load when needed.
├── examples/          ← Code to copy.
├── scripts/           ← Tools to run.
└── assets/            ← Templates for output.
```

### SKILL.md frontmatter

```
---
name: skill_identifier    ← snake_case
description: "This skill should be used when the user asks to 'DO X', 'DO Y'..."
metadata:
  qwenpaw:
    emoji: "ICON"         ← one emoji
    requires: {}
---
```

### What goes where

| Put in SKILL.md | Put in references/ |
|----------------|-------------------|
| Core workflow | Deep patterns |
| Must-know rules | Edge cases |
| Resource pointers | Full examples |

Keep SKILL.md under 1500 words. Move details to references/.

## WORKFLOW

### Step 1: Understand

Ask user:
- "What should this skill do?"
- "What will user say to trigger it?"

Get clear purpose. No ambiguity. If unclear, ask more.

### Step 2: Write

1. Write resources first (references/, examples/, scripts/, assets/)
2. Then write SKILL.md:
   - Frontmatter: name + third-person description with triggers
   - Body: imperative steps. Short. One thing per line.
   - Reference all resources at bottom

### Step 3: Validate

Pick the validation tool for your platform:

**Linux/Mac** → Run `scripts/validate-skill.sh <skill-dir>`
**Windows** → Run `..\self-review\scripts\validate.ps1 -SkillDir <skill-dir>`

The validator checks:

- Frontmatter: name + description exist
- Description: third person, trigger phrases
- Body: imperative form, no "you should"
- Resources: all referenced files exist
- Directory: organized correctly

Then run this checklist manually:

- [ ] All checks above pass
- [ ] No circular dependencies (does this skill reference itself?)
- [ ] Self-Review skill used for final quality gate (if Self-Review exists)

### Step 4: Iterate

Use skill. Find gaps. Fix. Repeat.

Common fixes:
- Weak triggers → add more trigger phrases
- Too long → move details to references/
- Missing examples → add to examples/

## COMMON MISTAKES

| Mistake | Fix |
|---------|-----|
| `description: "Guide for skills"` | `description: "This skill should be used when user asks to 'create a skill'..."` |
| "You should do X first" | "Do X first" |
| 5000 words in SKILL.md | 1500 words in SKILL.md. Rest in references/ |

## RESOURCES

- **`references/creation-methodology.md`** — Deep patterns and edge cases. Use when SKILL.md not enough.
- **`examples/skill-template/SKILL.md`** — Blank template. Copy to start new skill.
- **`scripts/validate-skill.sh`** — Linux/Mac validator. Run as `bash validate-skill.sh <skill-dir>`.
- **`../self-review/scripts/validate.ps1`** — Windows validator. Run as `powershell -File validate.ps1 -SkillDir <skill-dir>`.
- **`../self-review/`** — Optional final quality gate. Run Self-Review after create.
