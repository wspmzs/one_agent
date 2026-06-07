#!/bin/bash
# scan-secrets.sh — Scan text for API keys, passwords, tokens, secrets
#
# Usage:
#   echo "some text with sk-abc123..." | bash scan-secrets.sh
#   cat file.txt | bash scan-secrets.sh
#
# Exit codes:
#   0 — No secrets found
#   2 — Secrets found (prints redacted version to stdout)

set -euo pipefail

INPUT=$(cat)

# Patterns to detect
PATTERNS=(
  # OpenAI / Anthropic / generic API keys
  'sk-[a-zA-Z0-9_\-]{20,}'
  # Google API keys
  'AIza[0-9A-Za-z\-_]{35,}'
  # AWS keys
  'AKIA[0-9A-Z]{16}'
  # Generic bearer tokens
  '[Bb]earer\s+[A-Za-z0-9._\-]{20,}'
  # Password assignments
  '(password|pwd|passwd|secret)\s*[:=]\s*['"'"'"]?[a-zA-Z0-9_\-!@#$%^&*()]{8,}'
  # Private paths (home dirs)
  '/Users/[a-zA-Z0-9_\-]+/'
  '/home/[a-zA-Z0-9_\-]+/'
  'C:\\\\Users\\\\[a-zA-Z0-9_\-]+\\\\'
)

SECRETS_FOUND=0
OUTPUT="$INPUT"

for pattern in "${PATTERNS[@]}"; do
  if echo "$OUTPUT" | grep -qE "$pattern"; then
    SECRETS_FOUND=1
    # Replace matches with [REDACTED]
    OUTPUT=$(echo "$OUTPUT" | sed -E "s/$pattern/[REDACTED]/g")
  fi
done

if [ "$SECRETS_FOUND" -eq 1 ]; then
  echo "$OUTPUT"
  exit 2
fi

echo "$OUTPUT"
exit 0
