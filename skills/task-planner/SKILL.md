---
name: task_planner
description: "This skill should be used when the user asks to 'plan this', 'make a plan', 'break down the task', 'what are the steps', 'how should I approach', 'task breakdown', 'create a plan', 'project plan', 'estimate effort', 'what's the scope', 'outline the work', 'steps to follow'. Also when given a complex multi-step task that needs structured decomposition."
metadata:
  qwenpaw:
    emoji: "📋"
    requires: {}
---

# TASK PLANNER

## WHAT

Break complex tasks into structured plans.
Define phases, tasks, effort, dependencies.
Track progress. Iterate as plans change.

Prevents: missing steps, wrong order, scope creep.

## WHEN TO PLAN

Always plan when task has 3+ steps or crosses multiple domains.
Skip planning only if user explicitly says "no plan".

Minimal plan (3-5 bullets) is still better than no plan.

## WORKFLOW

### Step 1: Understand the Goal

Restate user request in one sentence.
Confirm with user if unclear.

### Step 2: Probe Environment

Use **Environment Probe** skill to check available tools.
Plan tasks based on real capabilities.
Don't plan for tools that don't exist.

### Step 3: Decompose

Break the goal into phases, then tasks.

**Phases** group related tasks. Order by dependency.
**Tasks** are single actions. Each should be:
- Actionable: "Create SKILL.md" not "Make skill better"
- Verifiable: someone can tell if it's done
- Independent: one person/agent can do it alone

### Step 4: Add Estimates

Tag each task with effort:

| Tag | Meaning | Duration |
|-----|---------|----------|
| XS | 1-2 steps | <5 min |
| S | 3-5 steps | <15 min |
| M | 5-15 steps | <1 hr |
| L | Multiple files | 2-4 hr |
| XL | Cross-domain | >4 hr |

### Step 5: Identify Dependencies

Mark tasks that block other tasks.
A task can start only when its dependencies are done.

Format: `Task C → depends on Task A, B`

### Step 6: Present Plan

Output structured plan to user.
Ask for approval before executing.

### Step 7: Track Progress

Mark tasks as done/in progress/pending.
Update estimates as work reveals true scope.
Add follow-up tasks when original estimates were wrong.

## OUTPUT FORMAT

```
📋 Plan: [Goal]
  Environment: Node v20, Python 3.12

  Phase 1: Setup
    [1] Install deps          S  —  🟢 done
    [2] Configure project     S  depends on 1  🟢 done
    [3] Verify setup          XS depends on 1,2  🟡 in progress

  Phase 2: Build
    [4] Implement feature     M  depends on Phase 1  ⚪ pending
    [5] Write tests           S  depends on 4  ⚪ pending

  Progress: 2/5 done
```

## VALIDATE PLAN QUALITY

Before showing plan to user, check:

- [ ] Goal matches user request (not solving the wrong problem)
- [ ] Tasks are actionable (not vague)
- [ ] Dependencies make sense (no circular deps)
- [ ] Estimates fit task complexity
- [ ] No obvious gaps (something clearly missing)
- [ ] Environment supports the plan (tools exist)
- [ ] Phases have logical ordering

## RESOURCES

- **`references/planning-patterns.md`** — Deep patterns: plan depth, dependencies, risks, cross-skill integration
- **`examples/plan-template.md`** — Reusable plan template with table format

## INTEGRATION WITH OTHER SKILLS

- **Environment Probe** — Use in Step 2: check tools before planning
- **Skill Creator** — Use when plan includes creating new skills
- **MCP Configurator** — Use when plan includes adding MCP servers
- **Self-Review** — Use after each task to validate deliverable
