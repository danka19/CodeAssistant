---
name: task-router
description: "Classify ambiguous development requests before broad reading or delegation. Use when Codex must decide task type, minimum context, risk level, whether to keep work local, and which project subagents to use: analyst_architect, programmer, reviewer, or verifier. Do not use for clearly scoped small edits, direct answers, or tasks where the user already specified the exact file and action."
---

# Task Router

Classify before reading broadly.

## Output

Return this compact shape:

```text
TaskRoute
task_type:
risk_level:
delegate: yes | no
roles:
minimum_read:
write_set_guess:
checks_guess:
stop_conditions:
reasoning:
```

## Task Types

Use one:
- `direct-answer`: explain or answer without repo edits.
- `small-edit`: simple local change, usually no subagent.
- `implementation`: code or docs change.
- `architecture-investigation`: needs read-only mapping before edits.
- `review`: inspect diff/work and report findings.
- `verification`: run deterministic checks.
- `process-config`: update team, skills, agents, or workflow policy.

## Delegation Defaults

- Prefer no delegation for trivial single-file work.
- Prefer `analyst_architect` before implementation when ownership or architecture is unclear.
- Prefer one `programmer` per write set.
- Prefer `reviewer` after non-trivial changes.
- Prefer `verifier` for deterministic checks.
- Do not load unrelated docs or old project-specific skills.

## Risk Levels

- `low`: direct answer, docs wording, simple config.
- `medium`: implementation with localized tests or multiple files.
- `high`: architecture, data contracts, security, migrations, external effects, or ambiguous product decisions.

## Stop Conditions

Always include a stop condition when:
- task scope is unclear;
- required write set is not knowable yet;
- user intent conflicts with local docs;
- implementation would require a product, UX, architecture, or data-contract decision.

