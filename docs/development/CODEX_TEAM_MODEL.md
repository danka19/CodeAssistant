# Codex Team Model

Status: active
Audience: contributors and coding agents
Owner: repository maintainers
Update when: local Codex delegation rules, role models, or concurrency limits change

## Purpose

This document defines the project-local Codex collaboration model used while developing this repository.

## Team Shape

The root assistant remains the only orchestrator.

Direct child roles only:

- `analyst_architect`
- `programmer`
- `reviewer`
- `verifier`

Child agents must not create nested agent chains.

## Delegation Depth

```toml
[agents]
max_depth = 1
max_threads = 4
```

This keeps user intent, scope control, and final accountability at the root assistant layer.

## Delegation Rules

Keep work local when:

- the task is a small single-file edit;
- the answer is a direct explanation;
- context transfer would cost more than the work itself.

Delegate when:

- architecture or ownership needs read-only investigation;
- implementation and review should be separated;
- deterministic checks can run independently;
- a clean read-only review adds value.

## Work Order Contract

Every delegated task should use this compact structure:

```text
WorkOrder
role:
goal:
scope:
non_goals:
read_paths:
write_paths:
allowed_tools:
required_output:
stop_conditions:
token_budget:
```

Rules:

- keep `read_paths` and `write_paths` narrow;
- keep `write_paths` empty for read-only roles;
- state adjacent non-goals explicitly;
- include stop conditions for scope, ownership, and architecture uncertainty.

## Result Contract

Every child agent should return:

```text
AgentResult
status: done | blocked | needs_fix | not_started
summary:
files_read:
files_changed:
checks_run:
findings:
risks:
handoff_notes:
needs_user_decision:
```

## Model Policy

Use the configured role models unless there is an explicit escalation reason.

| Role | Model | Reasoning | Sandbox |
| --- | --- | --- | --- |
| `analyst_architect` | `gpt-5.4-mini` | `medium` | read-only |
| `programmer` | `gpt-5.3-codex` | `medium` | workspace-write |
| `reviewer` | `gpt-5.4` | `high` | read-only |
| `verifier` | `gpt-5.4-mini` | `low` | workspace-write |

`gpt-5.5` is the escalation model, not the default model.

Valid escalation reasons:

- high-impact architecture decision;
- security-sensitive change;
- data-loss or irreversible-state risk;
- conflicting source-of-truth docs or review findings;
- repeated failure on cheaper models;
- a decision that materially constrains future system design.

Invalid escalation reasons:

- routine code edits;
- docs-only updates;
- normal test or lint failures;
- broad file discovery;
- generic accuracy preference.

## Parallelism Rules

- no subagents for trivial work;
- one `programmer` at a time per write set;
- one `reviewer` for normal review;
- one `analyst_architect` for normal architecture mapping;
- use parallel work only when write sets and outputs are independent.

## Stop Rules

Any agent should stop and return `blocked` when:

- it needs files outside the assigned write set;
- dirty or conflicting work makes ownership unclear;
- a product, UX, architecture, or data-contract decision is missing;
- required commands fail in a way that changes the plan;
- the role would need to perform another role's responsibility to continue.
