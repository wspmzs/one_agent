# Skill Creation Methodology — Deep Reference

Complete methodology for creating QwenPaw skills, adapted from the skill-creator and plugin-dev patterns. Read this when the core SKILL.md workflow needs deeper guidance.

## The Philosophy of Skills

Skills are not documentation. They are **onboarding guides** that transform the agent from general-purpose into domain-specialized. The key insight: no model, no matter how capable, can fully possess procedural knowledge for every domain. Skills bridge that gap.

### What Makes a Great Skill

1. **Triggerable** — The right description ensures the skill loads at the right time
2. **Actionable** — Step-by-step instructions the agent can execute immediately
3. **Complete** — All necessary knowledge is either in the skill or in its resources
4. **Lean** — No fluff. Every sentence serves a purpose
5. **Self-contained** — The skill doesn't depend on other skills

## Deep Dive: Writing the Description

The description in YAML frontmatter is the **most important part** of a skill. It determines when the skill loads.

### The Third-Person Rule

```
✅ "This skill should be used when the user asks to..."
```

Reason: The description is metadata about the skill, read by the system to decide whether to load it. First-person ("I do X") or second-person ("Use this when you...") breaks the metadata convention.

### Strong vs Weak Triggers

**Weak triggers (avoid):**
```
"...for working with hooks."
"...when help is needed."
"...provides guidance."
```

**Strong triggers (use):**
```
"...the user asks to 'create a hook', 'add a PreToolUse hook', 'validate tool use'..."
"...mentions 'PreToolUse', 'PostToolUse', 'Stop' hook events..."
```

### How to Identify Triggers

Ask these questions to find good trigger phrases:
1. What exact words will the user say?
2. What exact words would the agent think?
3. What synonyms or variations exist?

Collect 5-10 specific phrases and include the most important ones in the description.

## Deep Dive: Writing the Body

### Imperative/Infinitive Form

**Correct (imperative):**
```
To create a hook, define the event type.
Configure the MCP server with authentication.
Validate settings before use.
Read the configuration file first.
```

**Incorrect (second person):**
```
You should create a hook by defining the event type.
You need to configure the MCP server.
You must validate settings before use.
```

### Objective, Instructional Language

Focus on what to do, not who should do it:

```
✅ "Parse the frontmatter using sed."
✅ "Extract fields with grep."
✅ "Validate values before use."

❌ "You can parse the frontmatter using sed..."
❌ "Claude should extract fields..."
❌ "The user might validate values..."
```

### Structure Patterns

**Pattern 1: Overview → Steps → Validation**
```
# WHAT
[2-3 sentence overview]

# WORKFLOW
1. [Step 1]
2. [Step 2]
3. [Step 3]

# VALIDATION
Checklist before delivery
```

**Pattern 2: Problem → Solution → Details**
```
# THE PROBLEM
[What goes wrong without this skill]

# THE SOLUTION
[How this skill fixes it]

# EXECUTION
[Step-by-step]
```

**Pattern 3: Reference format (for tool skills)**
```
# CAPABILITIES
[List what the skill can do]

# WHEN TO USE
[Trigger conditions]

# HOW TO USE
[Workflow with tool-specific instructions]
```

## Deep Dive: Progressive Disclosure

### Why It Matters

Context window is finite. Loading 5000 words of skill content when only 800 words are needed wastes tokens and dilutes focus.

### The Three Levels

**Level 1 — Metadata (always in context):**
- `name` field
- `description` field
- ~50-100 words total

**Level 2 — SKILL.md body (loaded when triggered):**
- Core workflow
- Essential knowledge
- Resource pointers
- 800-2000 words

**Level 3 — Resources (loaded as needed):**
- references/ — detailed patterns, deep guides
- examples/ — working code to read
- scripts/ — utilities to execute

### Deciding What Goes Where

**In SKILL.md:**
- The "why" — purpose and value
- The "what" — core procedure
- The "how to find more" — resource pointers
- Quick reference — tables, checklists

**In references/:**
- Deep patterns with variations
- Multiple approaches to same problem
- Historical context or migration guides
- Complete API documentation

**In examples/:**
- Runnable code
- Complete configuration files
- Templates the user can copy

**In scripts/:**
- Deterministic validation logic
- Repeatedly rewritten code
- Complex parsing or transformation

## Deep Dive: Resource Organization

### When to Create Each Resource Type

**Scripts (`scripts/`)**

Create when the same code is being rewritten repeatedly or deterministic reliability is needed.

Examples:
- `scripts/validate-skill.sh` — skill validation
- `scripts/rotate-pdf.py` — PDF rotation
- `scripts/parse-frontmatter.sh` — YAML parsing

Benefits: Token efficient, deterministic, can be executed without loading into context.

**References (`references/`)**

Create for documentation the agent should reference while working.

Examples:
- `references/patterns.md` — common patterns
- `references/api-spec.md` — API documentation
- `references/company-policies.md` — domain knowledge

Best practices:
- Keep individual files focused on one topic
- If files are large (>10k words), include grep/search patterns in SKILL.md
- Information should live in either SKILL.md or references, not both

**Examples (`examples/`)**

Create for working code the agent can read, copy, or reference.

Examples:
- `examples/validate-write.sh` — complete hook script
- `examples/stdio-server.json` — MCP configuration
- `examples/skill-template/` — reusable skill template

**Assets (`assets/`)**

Create for files used in the skill's output, not loaded into context.

Examples:
- `assets/logo.png` — brand assets
- `assets/slides.pptx` — presentation templates
- `assets/frontend-template/` — boilerplate code

## Edge Cases in Skill Creation

### Skill Doesn't Trigger

**Symptoms:** Agent doesn't load the skill when expected
**Causes:**
- Description missing key trigger phrases
- Trigger phrases don't match what user actually says
- Description uses wrong person (second instead of third)
- Name too generic or conflicting

**Fixes:**
- Add the exact phrases the user says
- Use a third-person "This skill should be used when..."
- Test with the actual words, not ideal words
- Consider renaming if too generic

### Skill Content Too Long

**Symptoms:** Agent wastes tokens on unnecessary detail
**Causes:**
- Everything in SKILL.md instead of references/
- Examples inline instead of in examples/
- Redundant explanations

**Fixes:**
- Move detailed patterns to references/
- Move code samples to examples/
- Cut repetitive explanations
- Keep SKILL.md under 2000 words

### Skill Content Too Short

**Symptoms:** Agent doesn't have enough context to execute
**Causes:**
- Missing step-by-step workflow
- No edge case handling
- No output format defined

**Fixes:**
- Add explicit workflow steps
- Include common edge cases
- Define what "done" looks like
- Add validation criteria

### Writing Style Inconsistency

**Symptoms:** Mixed imperative and second person
**Causes:**
- Copy-paste from different sources
- No style guide followed

**Fixes:**
- Review entire skill for second person ("you should", "you need to")
- Convert all instructions to imperative form
- Check description for third person

## Quality Checklist (Extended)

### Structure
- [ ] SKILL.md file exists
- [ ] YAML frontmatter has name and description
- [ ] Markdown body present and substantial
- [ ] All referenced files actually exist
- [ ] No orphaned resource files

### Description
- [ ] Uses third person ("This skill should be used when...")
- [ ] Includes specific trigger phrases (5+ minimum)
- [ ] Lists concrete user scenarios
- [ ] Not vague or generic

### Writing Quality
- [ ] Body uses imperative/infinitive form throughout
- [ ] Body focused and lean (800-2000 words)
- [ ] Detailed content moves to references/
- [ ] Examples are complete and working
- [ ] Scripts are documented and executable

### Progressive Disclosure
- [ ] Core concepts in SKILL.md
- [ ] Detailed docs in references/
- [ ] Working code in examples/
- [ ] Utilities in scripts/
- [ ] SKILL.md references all resources

### Testing
- [ ] Skill triggers on expected user queries
- [ ] Content helps agent complete the task
- [ ] No duplicated information across files
- [ ] Resources load when needed
