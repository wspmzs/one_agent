---
name: environment_probe
description: "This skill should be used when the user asks to 'check my environment', 'what tools do I have', 'probe the system', 'do I have Python installed', 'what OS are we on', 'list available tools', 'scan my system', 'what can I run', 'environment check', 'is {tool} available'. Also when the agent needs to know available tools before generating commands or scripts."
metadata:
  qwenpaw:
    emoji: "🖥️"
    requires: {}
---

# ENVIRONMENT PROBE

## WHAT

Probe local system. Find OS, tools, versions, paths.
Output structured data.
Use results to write compatible commands.

Prevents:
- Wrong OS commands (Linux cmd on Windows)
- Missing tool errors
- Wrong language scripts
- PATH-dependent failures

## TRIGGER

Run this skill when:
- User asks about system capabilities
- User says "check if I have X"
- User asks "what OS"
- Environment info needed before generating code

## WORKFLOW

### Step 1: Pick Script

Linux/Mac → `bash scripts/probe-env.sh`
Windows → `powershell -File scripts/probe-env.ps1`

If OS unknown, detect first:
- Linux/Mac: `uname -s`
- Windows: `ver` or check `%OS%`

### Step 2: Parse Output

Script returns JSON. Read and parse.

Key fields:
- `os` — OS type (Linux / Darwin / Windows_NT)
- `arch` — Architecture (x86_64 / AMD64 / arm64)
- `tools` — Object with tool name → `{installed, version}`
- `env` — Environment variables

### Step 3: Match Results to Task

Build command based on what's available:

| User wants | Check this tool | Use this |
|-----------|----------------|----------|
| Run script | python / python3 / node | Available runtime |
| Install package | pip / npm / winget / choco | Package manager |
| Build project | make / cmake / go build | Build system |
| Containers | docker / docker compose | Container tool |
| Git ops | git / gh | Git or CLI |
| Web dev | node / npm / deno / bun | Server runtime |

### Step 4: Handle Gaps

Tool missing → report and suggest install:
```
⚠️ Python not found
   Suggestion: Run `winget install Python.Python.3.12`
   Or download from https://python.org
```

Version too low → report minimum requirement:
```
⚠️ Node v16 found, needs v18+
   Suggestion: Use `nvm install 20` to upgrade
```

### Step 5: Run Probe Once Per Session

Cache results in memory. No need to re-probe.
If user installs a new tool mid-session, re-probe on request.

## OUTPUT FORMAT

When user asks "what do I have":

```
🖥️ Environment Probe
OS: Windows_NT 10.0.19045 (AMD64)

✅ Python 3.12.0
✅ Node v22.0.0
✅ Git 2.42.0
✅ Docker 24.0.6
⚠️  Python3 not found (use 'python' instead)
❌ Go not found
❌ Rust not found

ℹ️  PATH: 12 entries
```

## RESOURCES

- **`scripts/probe-env.sh`** — Linux/Mac probe script
- **`scripts/probe-env.ps1`** — Windows probe script
- **`references/probe-patterns.md`** — Deep patterns for complex cases
- **`examples/probe-output-example.json`** — Example JSON output

## VALIDATE

After probe, check:
- [ ] Script ran without error
- [ ] JSON parsed cleanly
- [ ] Commands match detected OS
- [ ] No unsupported tool references
- [ ] PATH-based tools included in analysis
