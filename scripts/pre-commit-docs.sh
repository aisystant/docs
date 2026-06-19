#!/usr/bin/env bash
# pre-commit hook для docs-репо (content validation).
#
# Установка:
#   ln -sf ../../scripts/pre-commit-docs.sh .git/hooks/pre-commit
#
# Проверяет:
#   1. Битые cross-repo ссылки (../../../PACK-personal/ontology.md#) — только staged .md
#   2. Ontology drift (если PACK-personal доступен рядом)
#   3. Didactic language (UB-1) — warning only
#   4. v4-lint porter — frontmatter подразделов (через DS-principles-curriculum/tools/v4-lint.py)

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOCS_DIR="${REPO_ROOT}/docs/ru/personal-design"
PACK_PERSONAL="${REPO_ROOT}/../PACK-personal/ontology.md"
V4_LINT="${REPO_ROOT}/../DS-principles-curriculum/tools/v4-lint.py"

HAS_ERROR=0

echo "=== Docs pre-commit validation ==="

# --- 1. Broken cross-repo links (только staged .md файлы) ---
echo "[1/4] Checking broken cross-repo links..."
STAGED_MD=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)

if [ ! -f "${PACK_PERSONAL}" ]; then
    echo "⚠️ SKIP: PACK-personal/ontology.md not found — cross-repo link check skipped"
elif [ -n "$STAGED_MD" ]; then
    BAD_LINKS=""
    while IFS= read -r f; do
        # Extract anchors and check if they exist in ontology
        while IFS= read -r anchor; do
            # anchor is like "../../../PACK-personal/ontology.md#something"
            # Extract the part after #
            tag="${anchor##*#}"
            # Convert URL-encoded/space to match markdown heading anchors
            # Simple check: grep for the anchor in ontology file
            if ! grep -q "^#*.*${tag}" "${PACK_PERSONAL}" 2>/dev/null; then
                BAD_LINKS="${BAD_LINKS}${f} -> ${tag}\n"
            fi
        done < <(grep -oE '\.\./\.\./\.\./PACK-personal/ontology\.md#[^ )\]]+' "$f" 2>/dev/null || true)
    done <<< "$STAGED_MD"

    if [ -n "$BAD_LINKS" ]; then
        echo "❌ FAIL: Found broken cross-repo links in staged files:"
        printf '%b' "$BAD_LINKS"
        HAS_ERROR=1
    else
        echo "✅ PASS: No broken cross-repo links in staged files"
    fi
else
    echo "✅ PASS: No staged markdown files to check"
fi

# --- 2. Ontology drift (only staged guide files) ---
echo "[2/4] Checking ontology drift..."
STAGED_GUIDES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^docs/ru/personal-design/.+\.md$' || true)
if [[ -n "$STAGED_GUIDES" && -f "${PACK_PERSONAL}" ]]; then
    if ! python3 -c "import frontmatter" 2>/dev/null; then
        echo "⚠️ SKIP: python-frontmatter не установлен — запустите: pip install python-frontmatter"
    else
        STAGE_DIR=$(mktemp -d)
        echo "$STAGED_GUIDES" | while IFS= read -r f; do
            mkdir -p "$STAGE_DIR/$(dirname "$f")"
            cp "$REPO_ROOT/$f" "$STAGE_DIR/$f"
        done
        if python3 "${REPO_ROOT}/scripts/sync-guide-to-ontology.py" \
            --check \
            --ontology "${PACK_PERSONAL}" \
            --guides-dir "$STAGE_DIR/docs/ru/personal-design" 2>/dev/null; then
            echo "✅ PASS: No ontology drift in staged files"
        else
            echo "❌ FAIL: Ontology drift detected in staged files"
            HAS_ERROR=1
        fi
        rm -rf "$STAGE_DIR"
    fi
elif [[ ! -f "${PACK_PERSONAL}" ]]; then
    echo "⚠️ SKIP: PACK-personal/ontology.md not found at ${PACK_PERSONAL}"
    echo "    (drift check skipped — run manually if needed)"
else
    echo "✅ PASS: No staged guide files to check"
fi

# --- 3. Didactic language (warning only) ---
echo "[3/4] Checking didactic language..."
PATTERNS="шаг|урок|внедрить|за [0-9]+ дней|implement|lesson|step"
if grep -riE "${PATTERNS}" "${DOCS_DIR}" 2>/dev/null; then
    echo "⚠️ WARN: Potential didactic language found (review manually)"
else
    echo "✅ PASS: No didactic language detected"
fi

# --- 4. v4-lint porter on staged subsection files ---
echo "[4/5] Checking v4-lint porter..."
STAGED_SUBSECTIONS=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^docs/ru/personal-design/.+\.md$' | grep -v -E '(index|README|SUMMARY|CHANGELOG)\.md$' || true)

if [[ -n "$STAGED_SUBSECTIONS" && -f "$V4_LINT" ]]; then
    echo "v4-lint: проверяю staged подразделы..."
    echo "$STAGED_SUBSECTIONS" | sed 's/^/  /'
    echo ""
    if ! python3 "$V4_LINT" porter $STAGED_SUBSECTIONS; then
        echo "❌ FAIL: v4-lint porter detected errors"
        HAS_ERROR=1
    else
        echo "✅ PASS: v4-lint porter passed"
    fi
elif [[ ! -f "$V4_LINT" ]]; then
    echo "⚠️ SKIP: v4-lint.py not found at ${V4_LINT}"
else
    echo "✅ PASS: No staged subsections to check"
fi

# --- 5. v4-lint subsection on staged subsection files (WP-322 Ф20) ---
echo "[5/5] Checking v4-lint subsection (pack_refs, ontology, degrees, typography)..."
if [[ -n "$STAGED_SUBSECTIONS" && -f "$V4_LINT" && -f "$PACK_PERSONAL" ]]; then
    echo "v4-lint subsection: проверяю staged подразделы..."
    echo "$STAGED_SUBSECTIONS" | sed 's/^/  /'
    echo ""
    if ! python3 "$V4_LINT" subsection $STAGED_SUBSECTIONS --ontology "$PACK_PERSONAL"; then
        echo "❌ FAIL: v4-lint subsection detected errors"
        HAS_ERROR=1
    else
        echo "✅ PASS: v4-lint subsection passed"
    fi
elif [[ ! -f "$V4_LINT" ]]; then
    echo "⚠️ SKIP: v4-lint.py not found at ${V4_LINT}"
elif [[ ! -f "$PACK_PERSONAL" ]]; then
    echo "⚠️ SKIP: ontology.md not found at ${PACK_PERSONAL}"
else
    echo "✅ PASS: No staged subsections to check"
fi

if [[ "$HAS_ERROR" -ne 0 ]]; then
    echo ""
    echo "❌ Pre-commit validation FAILED. Fix errors before committing."
    exit 1
fi

echo ""
echo "✅ Pre-commit validation PASSED."
exit 0
