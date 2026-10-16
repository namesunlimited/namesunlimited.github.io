#!/usr/bin/env bash
# Repeatable audit. Run from anywhere: bash audit/run_all.sh
# Requires: python3, pip install -r audit/requirements.txt, and `playwright install chromium`.
set -u
cd "$(dirname "$0")/.."
mkdir -p audit/evidence
rc=0
run() { name="$1"; shift; echo "== $name"; "$@" 2>&1 | tee "audit/evidence/$name.log"; s=${PIPESTATUS[0]}; [ $s -ne 0 ] && rc=1; echo "   exit=$s"; }
run js_syntax      bash -c 'node --check js/app.js && node --check js/names-data.js && echo "js syntax ok"'
run static_audit   python3 audit/static_audit.py --json audit/static_results.json
run e2e_audit      python3 audit/e2e_audit.py
run tools_audit    python3 audit/tools_audit.py
run perf_a11y      python3 audit/perf_a11y_audit.py
echo "overall exit=$rc (e2e reports Firefox/WebKit as BLOCKED when those browsers are not installed; that is not a pass)"
exit $rc
