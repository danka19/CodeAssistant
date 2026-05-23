---
name: verification-gate
description: "Run and report deterministic project checks such as tests, build, lint, typecheck, smoke commands, or config validation. Use when Codex needs verification evidence after implementation or before acceptance. Do not use for speculative review, code edits, dependency installation, or implementation."
---

# Verification Gate

Run only relevant checks.

Until the project stack is fixed, discover commands in this order:
1. package scripts or build files in the repo root;
2. canonical documented commands in `docs/development/DEVELOPMENT_AGENT_POLICY.md` and `AGENTS.md`;
3. targeted commands requested by the parent agent.

Report using the typed `VerificationResult` shape defined in project-local skill `team-handoff`.

Rules:
- Distinguish failed, skipped, and not run.
- Do not edit files.
- Do not install dependencies or use network without parent approval.
- Do not call partial verification complete.
- If a command is unavailable, report that instead of inventing a substitute.
- Prefer targeted checks over full-suite checks for small changes unless risk justifies more.

If the repository already defines a canonical default check list, use that as the baseline expectation and then narrow only when the parent task scope justifies it.

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
