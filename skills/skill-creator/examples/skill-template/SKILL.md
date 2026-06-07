---
name: your_skill_name
description: "This skill should be used when the user asks to 'TRIGGER_PHRASE_1', 'TRIGGER_PHRASE_2', 'TRIGGER_PHRASE_3'. Replace these with actual phrases the user would say."
metadata:
  qwenpaw:
    emoji: "📦"
    requires: {}
---

# YOUR SKILL NAME

## WHAT

1-2 sentences describing what this skill does and why it exists. Focus on the value to the agent and user.

## WHEN TO TRIGGER

List the specific conditions that should cause this skill to load:

- User says X
- Agent detects Y
- Context includes Z

## WORKFLOW

### Step 1: Understand the Request

Describe what to do first. Be specific.

1. Read the user input to understand the goal
2. Check if prerequisites are met
3. Confirm with user if anything is unclear

### Step 2: Execute the Core Task

Describe the main action. Use imperative form.

1. Run the first operation
2. Process the result
3. Apply transformations if needed

### Step 3: Validate the Output

Describe how to check the work is correct.

1. Verify X is correct
2. Check Y is complete
3. Ensure no errors in Z

### Step 4: Deliver to User

Describe how to present the result.

1. Format the output clearly
2. Include next steps or follow-up suggestions
3. Confirm the task is complete

## EDGE CASES

### Edge Case 1: Description
- Symptom: What goes wrong
- Handle: How to fix it

### Edge Case 2: Description
- Symptom: What goes wrong
- Handle: How to fix it

## VALIDATION CHECKLIST

Before delivering, confirm:
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

## RESOURCES

### Reference Files
- (Optional) **`references/filename.md`** — What this contains and when to use it

### Scripts
- (Optional) **`scripts/filename.sh`** — What this does

### Examples
- (Optional) **`examples/filename`** — What this demonstrates

---

## ✏️ INSTRUCTIONS FOR THE SKILL CREATOR

When using this template to create a new skill:

1. Copy this entire file to the new skill's directory
2. Replace ALL placeholder content:
   - `your_skill_name` → actual skill name (snake_case)
   - `TRIGGER_PHRASE_*` → actual phrases users say
   - `📦` → appropriate emoji
   - All section content → your skill's content
3. Delete this bottom section (after the `---` separator)
4. Delete resource sections your skill doesn't need
5. Run `scripts/validate-skill.sh` on the result
