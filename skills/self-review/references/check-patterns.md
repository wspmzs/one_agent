# Self-Review Check Patterns

Deep reference for each check. Use when SKILL.md not enough.

## Check 1: Goal Match — Deep Patterns

### How to find user's original goal

Look in conversation history:
1. User's FIRST message in session = session goal
2. User's most recent explicit request = current goal
3. If user says "actually, forget that, do THIS" → THIS is new goal

### Common goal mismatches

| User said | Agent did | Fix |
|-----------|-----------|-----|
| "Make a Python script" | Explained how Python works | Make the script |
| "Analyze this file" | Rewrote the file | Analyze, don't change |
| "Fix the bug" | Rewrote entire module | Fix just the bug |
| "Explain briefly" | Wrote 3 pages | Cut to 3 sentences |

### Verbatim request check

If user asked for specific format, words, or structure:
- Does output use exact same terms?
- Does output follow same structure?
- If user said "JSON output" → output must be valid JSON

## Check 2: Security Scan — Deep Patterns

### Secret patterns to scan

```
API keys:        sk-[a-zA-Z0-9]{20,}
                 AIza[0-9A-Za-z\-_]{35}
                 [A-Za-z0-9_-]{32,}=
Passwords:       password.*=.*['\"][^'\"]+['\"]
                 pwd.*=.*['\"][^'\"]+['\""]
Tokens:          [Bb]earer\s+[A-Za-z0-9._\-]+
Private paths:   /Users/[^/]+/
                 /home/[^/]+/
                 C:\\Users\\[^\\]+\\
```

### What to replace with

| Found | Replace with |
|-------|-------------|
| API key | `YOUR_API_KEY_HERE` |
| Password | `YOUR_PASSWORD_HERE` |
| Token | `YOUR_TOKEN_HERE` |
| Private path | `./path/to/file` |

### False positives

Not everything that looks like a key is a key:
- `sk-` prefix is common in example code
- Hash values in example outputs
- Placeholder patterns like `your-key-here`

When unsure: replace. Better safe than leak.

## Check 3: Code Validity — Deep Patterns

### Pseudo-code detection

Signs code is pseudo-code not real:
- `function doSomething()` without body
- `// ... existing code ...`
- `# TODO: implement this`
- Functions named `foo()`, `bar()`, `baz()`
- `some_magic_function()` that doesn't exist
- `process_data()` without implementation

Fix: implement properly or mark as pseudo-code with `<!-- THIS IS PSEUDO-CODE -->`.

### Common syntax errors

| Language | Common error |
|----------|-------------|
| Python | Missing colon after `if`, `def`, `for` |
| Python | Indentation inconsistent |
| JavaScript | Missing semicolons in critical places |
| JavaScript | Unclosed brace or bracket |
| Bash | Missing `fi` for `if` |
| Bash | Unclosed quote in string |
| JSON | Trailing comma |
| JSON | Single quotes instead of double |

## Check 4: Completeness — Deep Patterns

### Leftover markers

Scan for these in final output:
- `TODO` — unresolved task
- `FIXME` — known bug
- `PLACEHOLDER` — missing content
- `[...]` — omitted content
- `// ... rest of code ...` — incomplete example
- `I'll add X later` — unfinished promise

### Missing sections

If output follows a template or structure:
- Are all headings present?
- Are all promised sections filled?
- Does every "see below" have something below?

## Check 5: Format — Deep Patterns

### Markdown issues

- Code block without language tag: ` ``` ` → ` ```python `
- Broken table: column count mismatch
- Bare URL: wrap in `<>` or `[]()`
- HTML that should be markdown

### When to use each format

| Content | Format |
|---------|--------|
| Code | ` ```language code ``` ` |
| Filename | `` `file.py` `` |
| Key term | **bold** or *italic* |
| List | `- item` or `1. item` |
| Link | `[text](url)` |
| Warning | `> **Warning**: ...` |
