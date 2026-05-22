---
name: verification-gate
description: "Run and report deterministic project checks such as tests, build, lint, typecheck, smoke commands, or config validation. Use when Codex needs verification evidence after implementation or before acceptance. Do not use for speculative review, code edits, dependency installation, or implementation."
---

# Verification Gate

Run only relevant checks.

Until the project stack is fixed, discover commands in this order:
1. package scripts or build files in the repo root;
2. documented commands in project docs;
3. targeted commands requested by the parent agent.

Report:

```text
VerificationResult
commands_run:
passed:
failed:
skipped:
not_run:
evidence_summary:
likely_failure_area:
```

Rules:
- Distinguish failed, skipped, and not run.
- Do not edit files.
- Do not install dependencies or use network without parent approval.
- Do not call partial verification complete.
- If a command is unavailable, report that instead of inventing a substitute.
- Prefer targeted checks over full-suite checks for small changes unless risk justifies more.

## Common Discovery Commands

Use only when relevant:
- `rg --files`
- `Get-ChildItem`
- `git status --short`
- project package/build metadata inspection

## Stop Conditions

Return blocked when:
- verification needs dependency installation;
- verification needs network;
- command output implies implementation changes outside verification scope;
- a command would be destructive or mutate unrelated state.

