<#
.SYNOPSIS
  Detect system environment. Output JSON to stdout.
.DESCRIPTION
  Probes OS info, installed tools, and environment variables.
  Outputs structured JSON for the agent to parse.
.EXAMPLE
  powershell -File probe-env.ps1
#>

$ErrorActionPreference = 'Stop'

$result = [PSCustomObject]@{
    os       = [System.Environment]::OSVersion.Platform.ToString()
    os_ver   = [System.Environment]::OSVersion.VersionString
    arch     = if ([System.Environment]::Is64BitOperatingSystem) { "AMD64" } else { "x86" }
    path_count = [System.Environment]::GetEnvironmentVariable("PATH").Split(";").Count
    shell    = [System.Environment]::GetEnvironmentVariable("ComSpec")
    tools    = [PSCustomObject]@{}
    env      = [PSCustomObject]@{}
}

# --- Tool detection with Get-Command (Application only, no aliases) ---
function Test-CommandExists {
    param([string]$cmd)
    # Use -CommandType Application to skip PowerShell aliases/functions
    $null -ne (Get-Command $cmd -CommandType Application -ErrorAction SilentlyContinue)
}

function Get-ToolVersion {
    param([string]$cmd, [string]$flag)
    try {
        # Capture both stdout and stderr
        $ver = & $cmd $flag 2>&1 | ForEach-Object { "$_" } | Select-Object -First 3
        $text = ($ver -join ' ').Trim()
        # If output is empty or contains only non-ASCII garbage, return empty
        if (-not $text -or $text -match '^[^\x20-\x7E]+$') { return "" }
        return $text
    } catch {
        return "error: $($_.Exception.Message)"
    }
}

# Helper: check if a command actually works (handles Windows App shims)
function Test-CommandWorks {
    param([string]$cmd, [string]$flag="--version")
    try {
        $null = & $cmd $flag 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

$tools = @(
    @{name="python";   cmd="python";    flag="--version"}
    @{name="python3";  cmd="python3";   flag="--version"}
    @{name="pip";      cmd="pip";       flag="--version"}
    @{name="pip3";     cmd="pip3";      flag="--version"}
    @{name="node";     cmd="node";      flag="--version"}
    @{name="npm";      cmd="npm";       flag="--version"}
    @{name="git";      cmd="git";       flag="--version"}
    @{name="docker";   cmd="docker";    flag="--version"}
    @{name="go";       cmd="go";        flag="version"}
    @{name="java";     cmd="java";      flag="-version"}
    @{name="dotnet";   cmd="dotnet";    flag="--version"}
    @{name="curl";     cmd="curl.exe";  flag="--version"}
    @{name="winget";   cmd="winget";    flag="--version"}
    @{name="choco";    cmd="choco";     flag="--version"}
    @{name="scoop";    cmd="scoop";     flag="--version"}
    @{name="code";     cmd="code";      flag="--version"}
    @{name="make";     cmd="make";      flag="--version"}
    @{name="cmake";    cmd="cmake";     flag="--version"}
    @{name="rustc";    cmd="rustc";     flag="--version"}
    @{name="cargo";    cmd="cargo";     flag="--version"}
    @{name="ruby";     cmd="ruby";      flag="--version"}
    @{name="flutter";  cmd="flutter";   flag="--version"}
    @{name="deno";     cmd="deno";      flag="--version"}
    @{name="bun";      cmd="bun";       flag="--version"}
    @{name="yarn";     cmd="yarn";      flag="--version"}
    @{name="pnpm";     cmd="pnpm";      flag="--version"}
    @{name="conda";    cmd="conda";     flag="--version"}
    @{name="wsl";      cmd="wsl.exe";   flag="--version"}
    @{name="docker-compose"; cmd="docker-compose"; flag="--version"}
)

$toolObj = [PSCustomObject]@{}
foreach ($t in $tools) {
    $cmdExists = Test-CommandExists $t.cmd
    $version = ""
    $installed = $false

    if ($cmdExists) {
        $version = Get-ToolVersion $t.cmd $t.flag
        # If version empty (e.g. Windows App shim), verify command actually works
        if ($version -eq "" -or $version -match "^error:") {
            $works = Test-CommandWorks $t.cmd $t.flag
            if (-not $works) {
                $installed = $false
                $version = ""
            } else {
                $installed = $true
            }
        } else {
            $installed = $true
        }
    }

    $toolObj | Add-Member -MemberType NoteProperty -Name $t.name -Value ([PSCustomObject]@{
        installed = $installed
        version   = $version
    }) -Force
}
$result.tools = $toolObj

# --- Environment Variables ---
$envVars = @("USERPROFILE", "HOMEDRIVE", "HOMEPATH", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "USERNAME", "COMPUTERNAME", "OneDrive")
$envObj = [PSCustomObject]@{}
foreach ($var in $envVars) {
    $val = [System.Environment]::GetEnvironmentVariable($var)
    if ($val) {
        $envObj | Add-Member -MemberType NoteProperty -Name $var -Value $val -Force
    }
}
$result.env = $envObj

# --- Output as JSON ---
$result | ConvertTo-Json -Depth 3
