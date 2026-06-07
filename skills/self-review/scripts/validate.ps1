<#
.SYNOPSIS
  Validate any QwenPaw skill directory.
.DESCRIPTION
  Runs 9 checks: SKILL.md existence, YAML frontmatter, name field,
  third-person description, trigger phrases, imperative body,
  referenced files, resource directories, circular dependencies.
.PARAMETER SkillDir
  Path to the skill directory to validate.
  Defaults to the self-review skill directory.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File validate.ps1
  powershell -ExecutionPolicy Bypass -File validate.ps1 -SkillDir "skills\environment-probe"
#>

param(
    [string]$SkillDir = (Join-Path $PSScriptRoot "..\..\self-review")
)

$p = 0; $f = 0; $w = 0
$sk = Join-Path $SkillDir "SKILL.md"

if (-not (Test-Path $sk)) {
    Write-Host "FAIL SKILL.md not found at $sk" -ForegroundColor Red
    exit 1
}

$c = Get-Content $sk -Raw

# Extract skill name from frontmatter dynamically
$fm = if ($c -match '^---([\s\S]*?)---') { $Matches[1].Trim() } else { "" }
$skillName = ""
if ($fm -match 'name:\s*"?(\S[^"\r\n]*)') {
    $skillName = $Matches[1].Trim().Trim('"')
}
if ([string]::IsNullOrEmpty($skillName)) { $skillName = "unknown" }

Write-Host "=== Validate Skill: $skillName ===" -ForegroundColor Cyan
Write-Host ""

# 1. SKILL.md exists
if (Test-Path $sk) { $p++; Write-Host "  OK SKILL.md exists" -ForegroundColor Green }
  else { $f++; Write-Host "  FAIL SKILL.md not found" -ForegroundColor Red }

# 2. YAML frontmatter
if (-not [string]::IsNullOrEmpty($fm)) { $p++; Write-Host "  OK YAML frontmatter" -ForegroundColor Green }
  else { $f++; Write-Host "  FAIL no frontmatter" -ForegroundColor Red }

# 3. name field (dynamic)
if ($fm -match 'name:\s+\S') { $p++; Write-Host "  OK name: $skillName" -ForegroundColor Green }
  else { $f++; Write-Host "  FAIL name missing or empty" -ForegroundColor Red }

# 4. Third person description
if ($c -match 'description:\s+"This skill should be used') {
    $p++; Write-Host "  OK third person description" -ForegroundColor Green
} else {
    # Check if description exists at all
    if ($fm -match 'description:\s+"') {
        $w++; Write-Host "  WARN description exists but may not start with 'This skill should be used'" -ForegroundColor Yellow
    } else {
        $f++; Write-Host "  FAIL description missing or not in third person" -ForegroundColor Red
    }
}

# 5. Trigger phrases (quoted)
$t = [regex]::Matches($c, "'[^']+'").Count
if ($t -ge 5) { $p++; Write-Host "  OK $t trigger phrases" -ForegroundColor Green }
  elseif ($t -ge 3) { $w++; Write-Host "  WARN only $t triggers (min 5 recommended)" -ForegroundColor Yellow }
  else { $w++; Write-Host "  WARN only $t triggers (min 3 required)" -ForegroundColor Yellow }

# 6. Imperative body (no "you should")
$body = ($c -split '---' | Select-Object -Index 2)
$secondPerson = @('you should','you need','you can','you must') | Where-Object { $body -match "(?i)$_" }
if ($secondPerson.Count -eq 0) { $p++; Write-Host "  OK body: imperative, no second person" -ForegroundColor Green }
  else { $w++; Write-Host "  WARN second person found: $($secondPerson -join ', ')" -ForegroundColor Yellow }

# 7. Referenced files exist (any extension)
# Capture text in parentheses that looks like a file path
$refs = [regex]::Matches($c, '\(([^)]+)\)') |
    ForEach-Object { $_.Groups[1].Value.Trim() } |
    # Take last "word" in the parens (after space/comma/slash)
    ForEach-Object {
        $parts = $_ -split '[ ,;]'
        $parts[-1].Trim()
    } |
    Where-Object { $_ -match '^[\w./\\-]+\.\w{2,4}$' -and $_ -notmatch '^https?://' } |
    # Exclude common config files referenced externally
    Where-Object { $_ -notin @('agent.json','config.json','settings.json','package.json','pyproject.toml') }
$missing = 0
foreach ($r in $refs) {
    $rp = Join-Path $SkillDir $r
    if (-not (Test-Path $rp)) { $missing++; Write-Host "  WARN missing: $r" -ForegroundColor Yellow }
}
if ($missing -eq 0) { $p++; Write-Host "  OK all $($refs.Count) referenced files exist" -ForegroundColor Green }
  else { $w++; Write-Host "  WARN $missing of $($refs.Count) refs missing" -ForegroundColor Yellow }

# 8. Resource directories
$dirs = @('references','examples','scripts')
foreach ($d in $dirs) {
    $dp = Join-Path $SkillDir $d
    if (Test-Path $dp) {
        $fc = (Get-ChildItem $dp -Recurse -File).Count
        if ($fc -gt 0) { $p++; Write-Host "  OK $d/ ($fc files)" -ForegroundColor Green }
          else { $w++; Write-Host "  WARN $d/ empty" -ForegroundColor Yellow }
    }
}

# 9. Self-reference check (circular dependency)
$bodyLower = $body.ToLower()
$skillNameLower = $skillName.ToLower()
# Check for self-reference by name (in snake_case or display form)
if ($bodyLower -match "\b$skillNameLower\b") {
    $w++; Write-Host "  WARN body self-references '$skillName'" -ForegroundColor Yellow
} else {
    $p++; Write-Host "  OK no self-reference in body" -ForegroundColor Green
}

Write-Host ""
Write-Host "PASS: $p | FAIL: $f | WARN: $w" -ForegroundColor Cyan
if ($f -gt 0) { Write-Host "RESULT: ISSUES FOUND" -ForegroundColor Red }
  else { Write-Host "RESULT: CLEAN" -ForegroundColor Green }
