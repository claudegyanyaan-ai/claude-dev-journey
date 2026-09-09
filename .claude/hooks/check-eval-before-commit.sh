#!/usr/bin/env bash
# PreToolUse hook: before a `git commit` Bash call, run the eval suite for
# real and block the commit if the pass rate is below THRESHOLD.
#
# This is the "gate on real test results, not a self-report" hook for
# Project 11 (see PLAN.md's Project 11 row). It doesn't trust a claim that
# tests pass -- it re-runs run_eval.py itself, right now, and reads that
# fresh result.

set -u

THRESHOLD=100   # required pass rate, in percent (100 = every case must pass)

input="$(cat)"

# Defense in depth: settings.json's handler-level `if` already scopes this
# hook to `git commit` commands; re-check the actual command string too, in
# case that filtering behaves differently across versions (same pattern as
# post-commit-push-reminder.sh).
command_str="$(printf '%s' "$input" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1)"
case "$command_str" in
  *"git commit"*) : ;;
  *) exit 0 ;;
esac

EVAL_DIR="${CLAUDE_PROJECT_DIR}/11-eval-observability-harness"
PYTHON="${CLAUDE_PROJECT_DIR}/10-multi-agent-orchestration/.venv/Scripts/python.exe"

if [ ! -f "$PYTHON" ]; then
  echo "Eval gate: can't find the venv Python at $PYTHON -- blocking commit until the eval can actually run." >&2
  exit 2
fi

output="$("$PYTHON" "$EVAL_DIR/run_eval.py" 2>&1)"
status=$?

if [ $status -ne 0 ]; then
  echo "Eval gate: run_eval.py failed to complete (exit $status) -- blocking commit, can't verify anything passed." >&2
  printf '%s\n' "$output" | tail -n 20 >&2
  exit 2
fi

summary="$(printf '%s\n' "$output" | grep -E '^=== [0-9]+/[0-9]+ passed ===$' | tail -1)"
passed="$(printf '%s\n' "$summary" | grep -oE '[0-9]+' | sed -n '1p')"
total="$(printf '%s\n' "$summary" | grep -oE '[0-9]+' | sed -n '2p')"

if [ -z "${passed:-}" ] || [ -z "${total:-}" ] || [ "$total" -eq 0 ]; then
  echo "Eval gate: couldn't parse a pass/total summary out of run_eval.py's output -- blocking commit." >&2
  printf '%s\n' "$output" | tail -n 20 >&2
  exit 2
fi

pct=$(( passed * 100 / total ))

if [ "$pct" -lt "$THRESHOLD" ]; then
  echo "Eval gate: $passed/$total passed ($pct%) -- below the ${THRESHOLD}% threshold. Commit blocked." >&2
  printf '%s\n' "$output" | grep '\[FAIL\]' >&2
  exit 2
fi

echo "Eval gate: $passed/$total passed ($pct%) -- commit allowed."
exit 0
