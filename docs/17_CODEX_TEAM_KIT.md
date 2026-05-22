# 17 Codex Team Kit

Version: v1.0
Status: active
Last updated: 2026-05-22

---

## 0. Purpose

This document defines the project-local Codex team model for high-quality development without context sprawl.

The user talks to the root assistant. The root assistant owns task intake, context trimming, delegation, integration, and final reporting.

The team model must optimize for:
- clean context per subagent;
- typed work orders and typed results;
- bounded role responsibilities;
- limited parallelism;
- explicit model choice per role;
- no project-specific skill or subagent leakage across unrelated projects.

---

## 1. Delegation Depth

This project uses:

```toml
[agents]
max_depth = 1
max_threads = 4
```

Meaning:
- the root assistant may spawn direct child agents;
- child agents must not spawn more agents;
- there is no separate recursive orchestrator subagent;
- the root assistant acts as the product-facing assistant and practical orchestrator.

Reason:
- `max_depth = 1` prevents runaway fan-out;
- the root assistant keeps user intent and final accountability;
- subagents receive compact work orders instead of full chat history;
- work stays cheaper and easier to review.

---

## 2. Team Shape

Default team roles:

| Role | Agent name | Default use |
| --- | --- | --- |
| Root assistant | current chat session | Intake, scope, delegation, integration, final answer |
| Analyst / Architect | `analyst_architect` | Read-only investigation, architecture options, impact map |
| Programmer | `programmer` | Bounded implementation in one write set |
| Reviewer | `reviewer` | Read-only diff review, risks, missing checks |
| Verifier | `verifier` | Commands, tests, build/lint evidence, no code edits |

Do not create separate agents for every small concern. Spawn only when the task has a real parallelizable or role-separated need.

---

## 3. Role Boundaries

## 3.1 Root Assistant

Allowed:
- read project files needed for task intake and integration;
- decide whether delegation is useful;
- create short work orders;
- integrate child-agent outputs;
- edit files directly when the task is small or delegation would add overhead;
- ask the user when a product, architecture, or scope decision is not safely inferable.

Forbidden:
- passing full chat history to child agents by default;
- spawning agents for routine single-file edits;
- accepting child-agent conclusions without review;
- letting child agents make final product/scope decisions.

## 3.2 `analyst_architect`

Allowed:
- inspect files;
- map architecture, dependencies, risks, and affected paths;
- propose implementation plans and write-set boundaries.

Forbidden:
- editing files;
- making final product decisions;
- broad speculative rewrites.

## 3.3 `programmer`

Allowed:
- edit only the assigned write set;
- run targeted checks when requested;
- return exact changed files and verification notes.

Forbidden:
- expanding into neighboring files without explicit reassignment;
- editing docs/status files unless explicitly assigned;
- doing final review of its own work.

## 3.4 `reviewer`

Allowed:
- inspect diffs, changed files, tests, and claims;
- report correctness, regression, security, maintainability, and missing-test findings.

Forbidden:
- editing code or docs while acting as reviewer;
- approving scope drift because it seems useful;
- replacing the root assistant's final acceptance decision.

## 3.5 `verifier`

Allowed:
- run build, lint, typecheck, test, and smoke commands;
- summarize pass/fail output and likely fault locations.

Forbidden:
- editing project files;
- treating partial checks as full acceptance;
- hiding skipped or failed checks.

---

## 4. Typed Work Orders

Every delegated task must use this shape:

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
- `read_paths` and `write_paths` must be as narrow as practical;
- `write_paths` must be empty for read-only agents;
- `non_goals` must name adjacent work the agent must avoid;
- `stop_conditions` must include crossing write-set boundaries, unclear ownership, or a real product/architecture decision.

---

## 5. Typed Agent Results

Every subagent returns this shape:

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

Rules:
- summaries should stay under 200 tokens unless the parent asks for detail;
- include exact files, commands, and check status;
- never paste large code blocks unless the parent explicitly asks;
- if blocked, state the smallest next decision or dependency.

---

## 6. Model Policy

Model choice is fixed by role so routine work does not silently use the most expensive model.

| Agent | Model | Reasoning | Sandbox | Rationale |
| --- | --- | --- | --- | --- |
| Root assistant | project default | medium/high as needed | workspace-write | Owns intent and integration; may escalate reasoning only for complex architecture |
| `analyst_architect` | `gpt-5.4-mini` | `medium` | read-only | Read-heavy mapping is common and should be cheap; escalate only if architectural uncertainty remains |
| `programmer` | `gpt-5.3-codex` | `medium` | workspace-write | Coding-focused role; use a coding-optimized model without defaulting to the frontier model |
| `reviewer` | `gpt-5.4` | `high` | read-only | Review benefits from stronger reasoning, but does not need the most expensive model by default |
| `verifier` | `gpt-5.4-mini` | `low` | workspace-write | Runs deterministic checks and summarizes output; no need for expensive reasoning |

Do not use a frontier/highest-cost model for a role unless:
- the cheaper role model produced an unresolved blocker;
- the task has high architectural risk;
- the parent assistant states the reason before escalation.

---

## 7. Parallelism Policy

Default:
- no subagents for trivial work;
- one `analyst_architect` for unclear codebase questions;
- one `programmer` at a time per write set;
- one `reviewer` after implementation;
- one `verifier` after or alongside review when checks can run independently.

Hard limits:
- max concurrent threads: 4;
- max active programmers on overlapping write sets: 1;
- max reviewers for normal work: 1;
- max analyst agents for normal work: 1.

Use multiple agents only when their work is independent and their outputs can be merged without conflict.

---

## 8. Stop Rules

Any agent must stop and return `blocked` when:
- it needs files outside its assigned write set;
- it detects dirty or conflicting work not covered by the work order;
- the task implies a product, UX, architecture, or data-contract decision not already approved;
- required commands fail in a way that changes the implementation plan;
- the role would need to perform another role's responsibility to continue.

The root assistant then decides whether to ask the user, adjust scope, reassign, or keep the work local.

