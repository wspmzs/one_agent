---
name: self_review
description: "This skill should be used before delivering any output to the user. Trigger when: writing code, generating a file, sending a message, making a change. Also when user says 'check this', 'review this', 'is this right', 'look it over'. Run this skill automatically before every major output."
metadata:
  qwenpaw:
    emoji: "✅"
    requires: {}
---

# SELF-REVIEW

## RULES

**Never deliver raw output. Always review first.**

One job: catch mistakes before user sees them.

## THE 5 CHECKS

Run all 5. Every time. In order.

### Check 1: Goal Match

Does output do what user originally asked?

- Restate user's original goal in your head
- Compare to what you're about to deliver
- If mismatched: fix before output
- If partially matched: complete before output
- If user goal changed mid-conversation: use LATEST goal

Goal mismatch is the worst failure. User asked X. You did Y. User unhappy.

### Check 2: Security Scan

No secrets in output. Ever.

Scan for:
- API keys (sk-..., AIza..., etc.)
- Passwords, tokens, secrets
- Internal URLs, IPs, credentials
- Private file paths (user home dirs, temp dirs)

If found: remove. Replace with `[REDACTED]` or `YOUR_KEY_HERE`.

### Check 3: Code Validity

Is code real? Can it run?

Check for:
- Pseudo-code marked as real code (fake function names, placeholder logic)
- Missing imports or dependencies
- Syntax errors (unclosed brackets, mismatched quotes)
- Broken file paths in examples

If code can't run: fix it. Or mark clearly as pseudo-code.

### Check 4: Completeness

Is output finished? Nothing missing?

- All sections present (if template)
- All promised deliverables exist
- No `TODO`, `FIXME`, `PLACEHOLDER` left in final output
- No "I'll add this later" — add it now

### Check 5: Format

Does output look right?

- Markdown renders cleanly
- Code blocks have language tag (```python, ```bash)
- Tables align
- Links work (format, not content)

Bad format confuses user. Fix before deliver.

## WORKFLOW

```
1. HOLD output. Do not deliver yet.
2. Run Goal Match check.
3. Run Security Scan.
4. Run Code Validity check.
5. Run Completeness check.
6. Run Format check.
7. Pass all 5? Deliver.
8. Fail any? Fix. Re-run checks. Then deliver.
```

## EDGE CASES

**No original goal recorded**: Use the most recent explicit user request as goal.

**Short output (1 sentence)**: Run checks 1-2-5 only. Code checks skip.

**Long output (multiple files)**: Run checks on each file separately.

**User said "just do it, don't check":** Still check for security (check 2). Skip others if user explicitly insists.

**User same language as output**: Goal match must compare in user's language, not translated.

## SELF-CHECK PROTOCOL

When delivering review results to user, output:

```
✅ Self-Review passed
  Goal: [matches/OK]
  Security: [clean/OK]
  Code: [valid/OK]
  Complete: [yes/OK]
  Format: [clean/OK]
```

Include only if there were issues. Don't spam.

## RESOURCES

- **`references/check-patterns.md`** — Detailed patterns for each check. Edge cases and examples.
- **`scripts/scan-secrets.sh`** — Auto-scan text for API keys and secrets (Linux/Mac).
- **`scripts/validate.ps1`** — Run all 9 validation checks on any skill (Windows).
- **`examples/checklist-template.md`** — Template to use for manual review.
