# Task Planner — Deep Patterns

Read this when SKILL.md workflow is not enough for a complex plan.

## Pattern: Plan Depth Levels

Not every task needs the same level of planning.

**Level 1 — Quick outline (5 min task)**
- 3-5 bullet steps
- No dependencies
- No effort estimates
- Use when: user asks "how would I do X"

**Level 2 — Task list (30 min task)**
- 5-15 steps with descriptions
- Dependencies between steps
- Simple effort tags (small/medium/large)
- Use when: multi-step workflow, script creation

**Level 3 — Project plan (multi-hour/multi-day)**
- Phases with milestones
- 15+ tasks with subtasks
- Dependency graph
- Effort estimates (hours)
- Risks and unknowns
- Use when: full feature build, project setup

## Pattern: Dependency Resolution

When tasks depend on each other, list them:

```
Phase 1: Setup (no dependencies)
  A. Install tools           → done
  B. Configure project       → depends on A
  C. Verify setup            → depends on A, B

Phase 2: Core (depends on Phase 1)
  D. Implement feature X     → depends on C
  E. Write tests for X       → depends on D
```

Rule: Never start a task before its dependencies are resolved.
Use this to reorder tasks when user asks to skip ahead.

## Pattern: Effort Estimation

Estimates are relative, not absolute. Compare to known tasks.

| Tag | Meaning | Example |
|-----|---------|---------|
| XS | 1-2 steps, <5 min | Edit a config value |
| S | 3-5 steps, <15 min | Create one file |
| M | 5-15 steps, <1 hr | Build a feature |
| L | multiple files, 2-4 hr | Create a full skill |
| XL | cross-domain, >4 hr | Multi-agent setup |

For each task, add effort tag in brackets: `[M] Write MCP configurator skill`.

## Pattern: Task Planner + Other Skills

Task Planner works best when combined with other skills:

**+ Environment Probe**
- Before planning: probe available tools
- Plan tasks based on actual capabilities
- If Python not found, don't plan Python scripts

**+ Skill Creator**
- Plan skill creation in phases:
  1. Research (understand the domain)
  2. Create resources (scripts, references, examples)
  3. Write SKILL.md
  4. Validate
  5. Test

**+ MCP Configurator**
- Plan adds: check runtime → configure → validate → verify

**+ Self-Review**
- After executing each task, self-review the deliverable
- Before marking a task done, run checks

## Pattern: Unknowns and Risks

When a task has unknown effort or outcome, mark it clearly:

```
[?] Task: Deploy to production
    Unknown: server config, domain setup, SSL cert
    Risk: deployment may break existing services
    Action: research before starting
```

If too many unknowns, recommend a research phase before planning.

## Pattern: Iterative Refinement

Plans change. When a task takes longer than estimated:

1. Mark original task as done
2. Add follow-up task with revised estimate
3. Adjust downstream dependencies
4. Tell user: "Task X took longer than expected. Added follow-up Y."

Don't overwrite original plan. Keep history of changes.

## Edge Cases

**User provides their own plan**: Validate it, don't replace it.
Check for gaps, missing dependencies, unrealistic estimates.

**Task seems too simple for planning**: Still make a minimal plan.
A 3-step plan is better than no plan. It catches obvious gaps.

**User says "just do it, no plan"**: Ask once:
"Even a quick 3-step outline? Helps me avoid mistakes."
If they insist, skip planning.

**Multiple agents involved**: Mark which agent handles each task.
Use `chat_with_agent` delegation where appropriate.

**Plan spans multiple sessions**: Save plan to a file.
Use `memory/` or a dedicated plan file.
Reference it at start of each session.
