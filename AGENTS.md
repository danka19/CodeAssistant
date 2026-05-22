# AGENTS.md

Development-time instructions for agents working on this repository.

This file is for building the AI Dev Orchestrator project itself. It is not the runtime policy for the future orchestrated agents. Runtime agent behavior is documented in `docs/05_AGENT_ROLES.md`, `docs/16_MVP_DECISIONS.md`, and the security/workflow documents under `docs/`.

## Project Context

We are building a small Linux VPS-based AI Dev Orchestrator.

Target MVP flow:

```text
Telegram user
-> Intake Assistant
-> task_brief.yaml
-> Claude Planner
-> optional approval
-> Codex Implementer
-> tests
-> PR
-> Claude Reviewer
-> Telegram report
-> manual merge
```

The project must stay GitHub-first, small, auditable, and deployable on a single rented VPS. Do not turn it into a large enterprise platform.

## Current MVP Decisions

Follow `docs/16_MVP_DECISIONS.md` as the active decision record.

Fixed choices for the first MVP:

- runtime mode: `systemd`;
- language: Python;
- storage: SQLite plus file logs;
- GitHub auth: fine-grained Personal Access Token;
- Claude/Codex auth: interactive CLI login under Linux user `ai-orchestrator`;
- repo aliases: `codeassistant` and `sandbox-py`;
- checks: `compileall`, `pytest`, `ruff check`, `ruff format --check`;
- no auto-merge;
- no auto-deploy;
- no Kubernetes;
- no Docker Compose in the first MVP unless explicitly requested later.

## Before Making Changes

- Read the relevant docs before implementing:
  - `docs/01_MVP_SCOPE.md`;
  - `docs/02_ARCHITECTURE.md`;
  - `docs/03_WORKFLOW.md`;
  - `docs/04_SECURITY_MODEL.md`;
  - `docs/07_VPS_WORKER_SPEC.md`;
  - `docs/12_IMPLEMENTATION_ROADMAP.md`;
  - `docs/16_MVP_DECISIONS.md`.
- Identify the current phase from `docs/12_IMPLEMENTATION_ROADMAP.md`.
- Keep changes scoped to that phase.
- If a requested change conflicts with `docs/16_MVP_DECISIONS.md`, stop and surface the conflict.

## Implementation Rules

- Prefer simple Python modules over framework-heavy abstractions.
- Keep the first worker single-process unless a documented phase requires otherwise.
- Use SQLite for task state in MVP.
- Use `subprocess` wrappers for `git`, `gh`, Claude CLI, and Codex CLI.
- Make command execution explicit, logged, timeout-bound, and redacted.
- Keep all writes inside the configured project directories:
  - `/srv/ai-orchestrator/data`;
  - `/srv/ai-orchestrator/runs`;
  - `/srv/ai-orchestrator/repos`;
  - `/srv/ai-orchestrator/worktrees`.
- Do not introduce network services, queues, dashboards, Docker, Kubernetes, Temporal, or browser automation unless the roadmap phase explicitly changes.

## Role Boundaries

Do not collapse the runtime roles while implementing the system.

- Intake Assistant prepares `task_brief.yaml`; it must not run shell, write git changes, create PRs, or call Codex.
- Claude Planner creates `plan.md` or `architecture_plan.md`; it must not edit code.
- Codex Implementer edits files only inside the task worktree.
- Claude Reviewer reviews diff/logs/tests; it must not edit code.
- Human approves high-risk plans, dangerous actions, and all merges.

Represent these boundaries in code through separate modules, typed artifacts, and explicit state transitions. Do not rely on a single vague "agent" function.

## Security Rules

- Never store secrets in code, docs, prompts, logs, fixtures, or test snapshots.
- Never print full environment variables.
- Redact tokens, keys, auth headers, cookies, and private key material before logging.
- Do not add production secrets, payment access, deploy credentials, or `docker.sock` access.
- Do not require root for normal worker operation.
- Dangerous shell actions must be blocked or require approval.
- The orchestrator must never merge into `main`.

## Git And Files

- Work through branches and PRs.
- Do not rewrite unrelated files.
- Do not do opportunistic refactoring.
- Do not reformat the whole repo unless the task is specifically about formatting.
- Do not commit generated runtime logs, local SQLite databases, CLI auth state, or `.env` files.
- Add `.gitignore` entries before creating local runtime artifacts.

## Testing Expectations

For Python code, prefer tests around:

- SQLite schema and migrations;
- task state transitions;
- branch slug generation;
- command allowlist/blocklist;
- secret redaction;
- fake Claude/Codex runners;
- fake GitHub client;
- temporary git repo integration for worktree creation.

Run the configured checks when code changes:

```bash
python -m compileall src tests
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

If checks cannot run because the project is not bootstrapped yet, say that explicitly and provide manual verification steps.

## Documentation Rules

Update docs when behavior, architecture, security policy, state machine, CLI commands, config, or workflow changes.

Use these docs as canonical references:

- MVP decisions: `docs/16_MVP_DECISIONS.md`;
- task states: `docs/09_TASK_STATES.md`;
- logging: `docs/10_LOGGING_AND_OBSERVABILITY.md`;
- CI/review gates: `docs/11_CI_AND_REVIEW_GATES.md`;
- acceptance criteria: `docs/13_MVP_ACCEPTANCE_CRITERIA.md`.

Keep MVP and future expansion separate. Future ideas belong in `docs/15_FUTURE_EXPANSION.md`, not in the first implementation path.

## Done Criteria

A development task is done only when:

- the change matches the active roadmap phase;
- files changed are scoped and explainable;
- tests/checks ran, or a clear reason is documented;
- docs are updated when needed;
- no secrets are introduced;
- no auto-merge/deploy behavior is introduced;
- the final summary states what changed, how it was verified, and what remains open.

## Local Codex Team Configuration

This repository uses a project-local Codex team model.

## Default Flow

The root assistant is the only orchestrator. It talks to the user, trims context, creates work orders, integrates results, and writes the final answer.

Subagents are direct children only:
- `analyst_architect`
- `programmer`
- `reviewer`
- `verifier`

Do not create nested agent chains. Project config sets `max_depth = 1`.

## When To Delegate

Keep work local when:
- the task is a small single-file edit;
- the answer is a direct explanation;
- delegation would require more context transfer than the task itself.

Delegate when:
- architecture or ownership needs investigation;
- implementation and review should be separated;
- deterministic checks can run independently;
- a clean read-only review is valuable.

## Required Handoff Shape

Use `$team-handoff` for every delegated task.

Child agents receive a compact `WorkOrder`, not the whole conversation.
Child agents return `AgentResult`, not long prose dumps.

## Skill Policy

Use project-local skills only:
- `$task-router`
- `$team-handoff`
- `$implementation-protocol`
- `$review-protocol`
- `$verification-gate`

Do not use Stamp Room-specific skills in this repository.

## Model Policy

Use the configured role models unless there is a stated escalation reason:
- `analyst_architect`: `gpt-5.4-mini`, medium reasoning, read-only
- `programmer`: `gpt-5.3-codex`, medium reasoning, workspace-write
- `reviewer`: `gpt-5.4`, high reasoning, read-only
- `verifier`: `gpt-5.4-mini`, low reasoning, workspace-write

Do not use the frontier/highest-cost model for routine subagent work just for marginal accuracy.

Use `gpt-5.5` only as an explicit escalation model. The parent assistant must state the reason in the WorkOrder before using it.

Valid `gpt-5.5` escalation reasons:
- high-impact architecture decision;
- security-sensitive change;
- data-loss or irreversible-state risk;
- conflicting source-of-truth docs or review findings;
- repeated failure on cheaper models;
- a decision that materially constrains future system design.

Invalid `gpt-5.5` reasons:
- routine code edits;
- docs-only updates;
- normal test/lint failures;
- broad file discovery;
- desire for a small generic accuracy gain.

