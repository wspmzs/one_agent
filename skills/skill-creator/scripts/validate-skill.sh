#!/bin/bash
# =============================================================================
# validate-skill.sh — QwenPaw Skill Validation Script
#
# Usage:
#   bash validate-skill.sh <path-to-skill-directory>
#
# Example:
#   bash validate-skill.sh skills/my-new-skill
#
# Checks:
#   1. SKILL.md exists
#   2. YAML frontmatter has name and description
#   3. Description uses third person
#   4. Description includes trigger phrases
#   5. Body uses imperative/infinitive form (basic check)
#   6. All referenced files exist
# =============================================================================

set -euo pipefail

SKILL_DIR="${1:-}"
PASS=0
FAIL=0
WARN=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() { PASS=$((PASS + 1)); echo -e "  ${GREEN}✓${NC} $1"; }
fail() { FAIL=$((FAIL + 1)); echo -e "  ${RED}✗${NC} $1"; }
warn() { WARN=$((WARN + 1)); echo -e "  ${YELLOW}⚠${NC} $1"; }

# ---- Help ----
if [ -z "$SKILL_DIR" ] || [ "$SKILL_DIR" = "--help" ] || [ "$SKILL_DIR" = "-h" ]; then
    echo ""
    echo " QwenPaw Skill Validator"
    echo ""
    echo " Usage:"
    echo "   bash validate-skill.sh <path-to-skill-directory>"
    echo ""
    echo " Example:"
    echo "   bash validate-skill.sh skills/my-new-skill"
    echo ""
    exit 0
fi

echo ""
echo "════════════════════════════════════════════"
echo "  Validating Skill: $SKILL_DIR"
echo "════════════════════════════════════════════"
echo ""

# ---- Check 1: SKILL.md exists ----
SKILL_FILE="$SKILL_DIR/SKILL.md"
if [ -f "$SKILL_FILE" ]; then
    pass "SKILL.md exists at $SKILL_FILE"
else
    fail "SKILL.md not found at $SKILL_FILE"
    echo ""
    echo " Result: $PASS passed, $FAIL failed, $WARN warnings"
    echo "════════════════════════════════════════════"
    echo ""
    exit 1
fi

# ---- Read frontmatter ----
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$SKILL_FILE" 2>/dev/null || echo "")
if [ -z "$FRONTMATTER" ]; then
    fail "No YAML frontmatter found (must start and end with '---')"
fi

# ---- Check 2: name field ----
if echo "$FRONTMATTER" | grep -qE '^name:\s+'; then
    NAME_VALUE=$(echo "$FRONTMATTER" | grep -E '^name:\s+' | sed 's/^name:\s*//' | tr -d '"'"'" )
    pass "Frontmatter has 'name': $NAME_VALUE"
else
    fail "Frontmatter missing 'name' field"
fi

# ---- Check 3: description field ----
if echo "$FRONTMATTER" | grep -qE '^description:\s+'; then
    DESC_VALUE=$(echo "$FRONTMATTER" | grep -E '^description:\s+' | head -1 | sed 's/^description:\s*//' | tr -d '"'"'" | head -c 80)
    pass "Frontmatter has 'description': ${DESC_VALUE}..."
else
    fail "Frontmatter missing 'description' field"
fi

# ---- Check 4: Description uses third person ----
if [ -n "$DESC_VALUE" ]; then
    FULL_DESC=$(echo "$FRONTMATTER" | grep -E '^description:\s+' | sed 's/^description:\s*//')
    if echo "$FULL_DESC" | grep -qiE "This skill should be used"; then
        pass "Description uses third person ('This skill should be used...')"
    elif echo "$FULL_DESC" | grep -qiE "Use this skill|You should|you need to|you can use"; then
        warn "Description may use second person. Prefer 'This skill should be used when...'"
    else
        warn "Description person unclear. Consider 'This skill should be used when...'"
    fi
fi

# ---- Check 5: Description includes trigger phrases ----
if [ -n "$FULL_DESC" ]; then
    # Check for quoted trigger phrases
    TRIGGER_COUNT=$(echo "$FULL_DESC" | grep -o "'[^']*'" | wc -l)
    if [ "$TRIGGER_COUNT" -ge 3 ]; then
        pass "Description includes $TRIGGER_COUNT quoted trigger phrases"
    elif [ "$TRIGGER_COUNT" -ge 1 ]; then
        warn "Only $TRIGGER_COUNT quoted trigger phrases found. Aim for 3+ (e.g. 'create a skill', 'write a skill')"
    else
        warn "No quoted trigger phrases found in description. Add examples like 'create a skill', 'write a skill'"
    fi
fi

# ---- Check 6: Body uses imperative form (basic check) ----
# Extract body (content after frontmatter)
BODY=$(awk 'BEGIN { found=0; count=0 } /^---$/ { count++; if (count==2) { found=1; next } } found && count==2' "$SKILL_FILE")

SECOND_PERSON_COUNT=$(echo "$BODY" | grep -cE "\b(you should|you need|you can|you must|you might|you will)\b" 2>/dev/null || echo "0")
DIRECT_IMPERATIVE_COUNT=$(echo "$BODY" | grep -cE "^[A-Z][a-z]+ [a-z]" 2>/dev/null || echo "0")

if [ "$SECOND_PERSON_COUNT" -le 3 ]; then
    pass "Body has minimal second-person usage ($SECOND_PERSON_COUNT instances — good)"
else
    warn "Body has $SECOND_PERSON_COUNT second-person instances. Convert to imperative: 'Do X' not 'You should do X'"
fi

# ---- Check 7: Workflow steps present ----
STEP_COUNT=$(echo "$BODY" | grep -cE "^[0-9]+\.\s+" 2>/dev/null || echo "0")
if [ "$STEP_COUNT" -ge 5 ]; then
    pass "Body contains $STEP_COUNT numbered steps (clear workflow)"
elif [ "$STEP_COUNT" -ge 1 ]; then
    warn "Only $STEP_COUNT numbered steps found. Consider adding more structure"
else
    warn "No numbered steps found. Consider adding explicit step-by-step workflow"
fi

# ---- Check 8: Referenced files exist ----
# Look for markdown links referencing files
REF_FILES=$(echo "$BODY" | grep -oE '\([^)]*\.(md|sh|py|json|txt)\)' | sed 's/[()]//g' 2>/dev/null || echo "")
REF_COUNT=0
MISSING_COUNT=0
for ref in $REF_FILES; do
    # Resolve relative to skill directory
    FULL_PATH="$SKILL_DIR/$ref"
    if [ -f "$FULL_PATH" ] || [ -d "$FULL_PATH" ]; then
        REF_COUNT=$((REF_COUNT + 1))
    else
        # Try without the leading directory
        MISSING_COUNT=$((MISSING_COUNT + 1))
        warn "Referenced file not found: $ref (resolved: $FULL_PATH)"
    fi
done
if [ "$REF_COUNT" -gt 0 ]; then
    pass "$REF_COUNT referenced files confirmed existing"
fi

# ---- Check 9: Check for resource directories ----
for dir in references examples scripts assets; do
    if [ -d "$SKILL_DIR/$dir" ]; then
        ITEM_COUNT=$(find "$SKILL_DIR/$dir" -type f 2>/dev/null | wc -l)
        if [ "$ITEM_COUNT" -gt 0 ]; then
            pass "Resource directory '$dir/' exists with $ITEM_COUNT files"
        else
            warn "Resource directory '$dir/' exists but is empty"
        fi
    fi
done

# ---- Summary ----
echo ""
echo "════════════════════════════════════════════"
echo "  Results: $PASS passed | $FAIL failed | $WARN warnings"
echo "════════════════════════════════════════════"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo " ❌ Skill has critical issues. Fix before use."
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo " ⚠️  Skill passes but has warnings. Consider addressing them."
    exit 0
else
    echo " ✅ Skill looks good!"
    exit 0
fi
