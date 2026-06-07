<#
.SYNOPSIS
  Validate MCP configuration in agent.json.
.DESCRIPTION
  Checks: JSON syntax, mcp.clients structure, required fields,
  transport type validity, command existence hints.
.PARAMETER ConfigPath
  Path to agent.json. Defaults to workspace/job agent.json.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File validate-mcp-config.ps1
#>

param(
    [string]$ConfigPath = ""
)

$p = 0; $f = 0; $w = 0
$baseDir = Split-Path -Parent $PSScriptRoot

# Find agent.json
if (-not $ConfigPath) {
    $candidates = @(
        Join-Path $baseDir "..\..\agent.json"
        Join-Path $baseDir "..\..\workspaces\*\agent.json"
        "agent.json"
    )
    foreach ($c in $candidates) {
        $resolved = Resolve-Path $c -ErrorAction SilentlyContinue
        if ($resolved) { $ConfigPath = $resolved; break }
    }
}

if (-not $ConfigPath -or -not (Test-Path $ConfigPath)) {
    Write-Host "FAIL: agent.json not found" -ForegroundColor Red
    exit 1
}

Write-Host "Config: $ConfigPath" -ForegroundColor Cyan
Write-Host ""

# 1. Valid JSON
try {
    $raw = Get-Content $ConfigPath -Raw -Encoding UTF8
    $config = $raw | ConvertFrom-Json -ErrorAction Stop
    $p++; Write-Host "  OK valid JSON" -ForegroundColor Green
} catch {
    # Try with BOM handling
    try {
        $bytes = [System.IO.File]::ReadAllBytes($ConfigPath)
        $raw = [System.Text.Encoding]::UTF8.GetString($bytes)
        $config = $raw | ConvertFrom-Json -ErrorAction Stop
        $p++; Write-Host "  OK valid JSON (UTF-8 BOM)" -ForegroundColor Green
    } catch {
        $f++; Write-Host "  FAIL invalid JSON: $_" -ForegroundColor Red
        exit 1
    }
}

# 2. mcp.clients exists
if ($config.mcp -and $config.mcp.clients) {
    $p++; Write-Host "  OK mcp.clients section exists" -ForegroundColor Green
} else {
    $w++; Write-Host "  WARN no mcp.clients section (create it)" -ForegroundColor Yellow
    $config.mcp.clients = @{}
}

# 3. Check each client
$keys = $config.mcp.clients.PSObject.Properties.Name
$clientCount = $keys.Count
$p++; Write-Host "  OK $clientCount MCP client(s) configured" -ForegroundColor Green

$issues = 0
foreach ($key in $keys) {
    $client = $config.mcp.clients.$key
    $issuesForClient = @()

    # Required fields
    if (-not $client.name) { $issuesForClient += "missing name" }
    if ($null -eq $client.enabled) { $issuesForClient += "missing enabled" }
    if (-not $client.transport) { $issuesForClient += "missing transport" }

    # Transport validation
    if ($client.transport -eq "stdio") {
        if (-not $client.command) { $issuesForClient += "stdio needs command" }
        if ($client.command -eq "npx" -and ($null -eq $client.args -or $client.args.Count -eq 0)) {
            $issuesForClient += "npx needs args"
        }
    } elseif ($client.transport -ne "stdio" -and $client.transport -ne "streamable_http" -and $client.transport -ne "sse") {
        $issuesForClient += "invalid transport: $($client.transport)"
    }

    # URL required for HTTP/SSE transport
    if (($client.transport -eq "streamable_http" -or $client.transport -eq "sse") -and -not $client.url) {
        $issuesForClient += "$($client.transport) needs url"
    }

    if ($issuesForClient.Count -gt 0) {
        $issues++
        Write-Host "  WARN client '$key': $($issuesForClient -join '; ')" -ForegroundColor Yellow
    }
}

if ($issues -eq 0) { $p++; Write-Host "  OK all clients have required fields" -ForegroundColor Green }

Write-Host ""
Write-Host "PASS: $p | FAIL: $f | WARN: $w" -ForegroundColor Cyan
if ($f -gt 0) { Write-Host "RESULT: ISSUES FOUND" -ForegroundColor Red }
  else { Write-Host "RESULT: CLEAN" -ForegroundColor Green }
