#!/usr/bin/env bash
# probe-env.sh — Detect system environment. Output JSON.
# Usage: bash probe-env.sh
# Output: JSON to stdout. Errors to stderr.
set -euo pipefail

echo "{"

# --- OS Info ---
os=$(uname -s 2>/dev/null || echo "unknown")
arch=$(uname -m 2>/dev/null || echo "unknown")
echo "  \"os\": \"$os\","
echo "  \"arch\": \"$arch\","

# --- PATH Info ---
echo "  \"path_count\": $(echo "$PATH" | tr ':' '\n' | wc -l),"

# --- Shell ---
shell="${SHELL:-}"
if [ -z "$shell" ]; then
  shell=$(ps -p $$ -o comm= 2>/dev/null || echo "unknown")
fi
echo "  \"shell\": \"$shell\","

# --- Tool detection ---
# Format: name:command:version_flag
TOOLS=(
  "python3:python3:--version"
  "python:python:--version"
  "pip3:pip3:--version"
  "pip:pip:--version"
  "node:node:--version"
  "npm:npm:--version"
  "git:git:--version"
  "docker:docker:--version"
  "go:go:version"
  "rustc:rustc:--version"
  "cargo:cargo:--version"
  "java:java:-version"
  "gcc:gcc:--version"
  "g++:g++:--version"
  "make:make:--version"
  "cmake:cmake:--version"
  "curl:curl:--version"
  "wget:wget:--version"
  "gh:gh:--version"
  "code:code:--version"
  "ruby:ruby:--version"
  "php:php:--version"
  "perl:perl:--version"
  "swift:swift:--version"
  "kotlin:kotlin:-version"
  "flutter:flutter:--version"
  "deno:deno:--version"
  "bun:bun:--version"
  "yarn:yarn:--version"
  "pnpm:pnpm:--version"
  "poetry:poetry:--version"
  "pipenv:pipenv:--version"
  "conda:conda:--version"
  "jupyter:jupyter:--version"
)

echo "  \"tools\": {"
first=true
for entry in "${TOOLS[@]}"; do
  # Split by ':'
  IFS=':' read -r name cmd flag <<< "$entry"

  if ! $first; then echo ","; fi
  first=false

  if command -v "$cmd" &>/dev/null 2>&1; then
    # Get version. stderr to stdout for tools like java.
    ver=$($cmd $flag 2>&1 | head -3 | tr '\n' ' ' | sed 's/[[:space:]]*$//')
    # Escape JSON special chars
    ver="${ver//\\/\\\\}"
    ver="${ver//\"/\\\"}"
    printf '    "%s": {"installed": true, "version": "%s"}' "$name" "$ver"
  else
    printf '    "%s": {"installed": false, "version": ""}' "$name"
  fi
done

echo ""
echo "  }"

# --- Env Vars ---
echo "  ,\"env\": {"
env_first=true
for var in HOME USER LOGNAME DISPLAY TERM EDITOR LANG LC_ALL; do
  val="${!var:-}"
  if [ -n "$val" ]; then
    if ! $env_first; then echo ","; fi
    env_first=false
    val="${val//\\/\\\\}"
    val="${val//\"/\\\"}"
    printf '    "%s": "%s"' "$var" "$val"
  fi
done
echo ""
echo "  }"

echo "}"
