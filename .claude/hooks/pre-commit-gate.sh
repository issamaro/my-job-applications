#!/usr/bin/env bash
# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Block git commits inside a v6 feature workflow until TEST_RESULTS and INSPECTION_RESULTS show PASS/READY.

set -e

command -v jq >/dev/null || { echo 'jq required'; exit 1; }

check_payload() {
  local payload
  payload=$(cat)

  local cmd
  cmd=$(echo "$payload" | jq -r '.tool_input.command // ""')

  if ! echo "$cmd" | grep -Eq '^[[:space:]]*git[[:space:]]+commit\b'; then
    echo '{"hookSpecificOutput":{"permissionDecision":"allow"}}'
    return
  fi

  local cwd
  cwd=$(echo "$payload" | jq -r '.cwd // "."')

  local edit_log="$HOME/.claude/edit-log.jsonl"
  local v6_touched=0
  if [ -f "$edit_log" ] && grep -q 'workbench/' "$edit_log" 2>/dev/null; then
    v6_touched=1
  fi

  if [ "$v6_touched" = "0" ]; then
    echo '{"hookSpecificOutput":{"permissionDecision":"allow"}}'
    return
  fi

  local tr_file
  tr_file=$(find "$cwd/workbench" -name 'TEST_RESULTS_*.md' 2>/dev/null | head -1)
  local ir_file
  ir_file=$(find "$cwd/workbench" -name 'INSPECTION_RESULTS_*.md' 2>/dev/null | head -1)

  if [ -z "$tr_file" ]; then
    echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"v6 commit blocked: no TEST_RESULTS_*.md found under workbench/. Run test-runner before committing."}}'
    return
  fi

  if ! grep -q '^status: PASS' "$tr_file"; then
    echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"v6 commit blocked: TEST_RESULTS status is not PASS."}}'
    return
  fi

  if [ -z "$ir_file" ]; then
    echo '{"hookSpecificOutput":{"permissionDecision":"allow"}}'
    return
  fi

  if ! grep -Eq '^status: (PASS|READY)' "$ir_file"; then
    echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"v6 commit blocked: INSPECTION_RESULTS status is not PASS or READY."}}'
    return
  fi

  echo '{"hookSpecificOutput":{"permissionDecision":"allow"}}'
}

run_self_test() {
  local mock_noncommit='{"tool_input":{"command":"git status"},"cwd":"/tmp/__nope__"}'
  local out
  out=$(echo "$mock_noncommit" | check_payload)
  echo "$out" | jq -e '.hookSpecificOutput.permissionDecision == "allow"' >/dev/null || {
    echo "self-test FAIL: non-commit should pass through"
    return 2
  }

  local mock_commit_no_v6='{"tool_input":{"command":"git commit -m foo"},"cwd":"/tmp/__nope__"}'
  out=$(echo "$mock_commit_no_v6" | check_payload)
  echo "$out" | jq -e '.hookSpecificOutput.permissionDecision == "allow"' >/dev/null || {
    echo "self-test FAIL: commit outside v6 session should pass through"
    return 2
  }

  echo "self-test ok"
  return 0
}

if [ "${1:-}" = "--self-test" ]; then
  run_self_test
  exit $?
fi

check_payload
