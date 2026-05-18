#!/usr/bin/env bash
# pre-commit hook для docs-репо (content validation).
#
# Установка:
#   ln -sf ../../scripts/pre-commit-docs.sh .git/hooks/pre-commit
#
# Проверяет:
#   1. Битые cross-repo ссылки (../../../PACK-personal/ontology.md#)
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

# --- 1. Broken cross-repo links ---
echo "[1/4] Checking broken cross-repo links..."
if grep -r "../../../PACK-personal/ontology.md#" "${DOCS_DIR}" 2>/dev/null; then
    echo "❌ FAIL: Found broken cross-repo links (../../../PACK-personal/ontology.md#)"
    HAS_ERROR=1
else
    echo "✅ PASS: No broken cross-repo links"
fi

# --- 2. Ontology drift (if PACK-personal is available) ---
echo "[2/4] Checking ontology drift..."
if [[ -f "${PACK_PERSONAL}" ]]; then
    if python3 "${REPO_ROOT}/scripts/sync-guide-to-ontology.py" \
        --check \
        --ontology "${PACK_PERSONAL}" \
        --guides "${DOCS_DIR}" 2>/dev/null; then
        echo "✅ PASS: No ontology drift"
    else
        echo "❌ FAIL: Ontology drift detected"
        HAS_ERROR=1
    fi
else
    echo "⚠️ SKIP: PACK-personal/ontology.md not found at ${PACK_PERSONAL}"
    echo "    (drift check skipped — run manually if needed)"
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
echo "[4/4] Checking v4-lint porter..."
STAGED_SUBSECTIONS=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^docs/ru/personal-design/.+\.md$' || true)

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

if [[ "$HAS_ERROR" -ne 0 ]]; then
    echo ""
    echo "❌ Pre-commit validation FAILED. Fix errors before committing."
    exit 1
fi

echo ""
echo "✅ Pre-commit validation PASSED."
exit 0
