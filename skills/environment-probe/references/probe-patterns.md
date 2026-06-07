# Environment Probe — Deep Patterns

Read this when standard probe workflow is not enough.

## Pattern: Custom Probe

Need to check a tool not in default list? Run inline:

```
# Linux/Mac
command -v <tool> && <tool> --version

# Windows
powershell -Command "Get-Command <tool> -ErrorAction SilentlyContinue"
```

Add new tools to probe-env.sh or probe-env.ps1 permanently if used often.

## Pattern: Verify Specific Version

Tool exists but version matters:

```
# Check minimum version
python3 -c "import sys; ver=sys.version_info; print(ver >= (3,10))"

# Check Node version meets threshold
node -e "console.log(process.version >= 'v18')"
```

If version too low, report: "Tool X found (vX.Y), but requires vA.B+"

## Pattern: PATH Resolution

Agent writes command that fails with "command not found". Why?

1. Tool installed but not in PATH
2. Tool behind a version manager (nvm, pyenv, rbenv)
3. Tool path has spaces (Windows: "C:\Program Files\...")

Fix: Use full path from `where`/`Get-Command` output.

## Pattern: Version Manager Detection

Common tools managed by version switchers:

| Tool | Manager | Detection |
|------|---------|-----------|
| Node | nvm, fnm | `nvm ls`, `fnm ls` |
| Python | pyenv, conda | `pyenv versions`, `conda list` |
| Ruby | rbenv, rvm | `rbenv versions` |
| Java | sdkman, jenv | `sdk list java` |

If detected, note that `--version` may show currently active version only.

## Pattern: WSL Detection (Windows)

Windows with WSL can run Linux commands. Detect:

```
powershell -Command "wsl -l -v"
wsl -e bash -c "uname -a"
```

But WSL has its own filesystem and tools. Commands that mix Windows and WSL paths fail.

Rule: If WSL detected, ask user which environment to target.

## Pattern: Docker Environment

Docker adds complexity. Check:

```
# Docker running?
docker info --format '{{.ServerVersion}}'

# Docker Compose available?
docker compose version

# Container runtime?
docker info --format '{{.OSType}}'
```

If Docker not accessible, user may need Docker Desktop running.

## Pattern: Cross-Platform Command Generation

Based on probe results, choose right command style:

| OS | Script lang | Path sep | Line ending | Env var access |
|----|------------|----------|-------------|----------------|
| Linux | bash | / | \n | $VAR |
| macOS | bash/zsh | / | \n | $VAR |
| Windows | pwsh/cmd | \ | \r\n | %VAR% or $env:VAR |

## Edge Cases

**Empty PATH**: Rare but happens. Report as critical.

**Permission denied**: Tool exists but agent can't run it (no +x flag).
Fix: `chmod +x <path>` or report issue.

**Symlinks**: `command -v` returns symlink. Resolve with `readlink -f`.
Version from symlink may differ from actual binary behind it.

**Case sensitivity**: Windows tools may work with any case. Linux tools are case-sensitive.

**32-bit vs 64-bit**: On Windows, 32-bit processes see different PATH than 64-bit.
Recommend 64-bit detection unless user specifies 32-bit.

## When To Skip Probe

- User asks simple text question (not code/ops related)
- Task is purely conceptual (design, review, plan)
- User already specified exact tools to use
- Environment was already probed this session (cached)
