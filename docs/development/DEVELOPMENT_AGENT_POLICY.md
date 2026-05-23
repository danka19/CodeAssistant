# Development Agent Policy

Status: active
Audience: contributors and coding agents
Owner: repository maintainers
Update when: repository development workflow or contribution guardrails change

## Purpose

This document contains the detailed development-time rules for working on the AI Dev Orchestrator repository itself.

`AGENTS.md` is the short entrypoint. This file holds the fuller repository policy.

## Required Reading

Before implementing changes, read the relevant system documents:

- `docs/01_MVP_SCOPE.md`
- `docs/02_ARCHITECTURE.md`
- `docs/03_WORKFLOW.md`
- `docs/04_SECURITY_MODEL.md`
- `docs/07_VPS_WORKER_SPEC.md`
- `docs/12_IMPLEMENTATION_ROADMAP.md`
- `docs/16_MVP_DECISIONS.md`

Always identify the current phase in `docs/12_IMPLEMENTATION_ROADMAP.md` and keep changes scoped to that phase.

If a request conflicts with `docs/16_MVP_DECISIONS.md`, stop and surface the conflict.

## Implementation Rules

- Prefer simple Python modules over framework-heavy abstractions.
- Keep the first worker single-process unless a documented phase changes that.
- Use SQLite for MVP task state.
- Use explicit `subprocess` wrappers for `git`, `gh`, Claude CLI, and Codex CLI.
- Make command execution explicit, logged, timeout-bound, and redacted.
- Keep all orchestrator writes inside:
  - `/srv/ai-orchestrator/data`
  - `/srv/ai-orchestrator/runs`
  - `/srv/ai-orchestrator/repos`
  - `/srv/ai-orchestrator/worktrees`
- Do not introduce network services, queues, dashboards, Docker, Kubernetes, Temporal, or browser automation unless the roadmap phase changes.

## Role Boundary Rules

Do not collapse runtime roles while implementing the system.

- Intake Assistant prepares `task_brief.yaml` and must not run shell, write git changes, create PRs, or call Codex.
- Claude Planner creates `plan.md` or `architecture_plan.md` and must not edit code.
- Codex Implementer edits files only inside the task worktree.
- Claude Reviewer reviews diff, logs, and test results and must not edit code.
- Human approves high-risk plans, dangerous actions, and all merges.

Represent these boundaries with separate modules, typed artifacts, and explicit state transitions. Do not hide them behind one vague agent function.

## Security Rules

- Never store secrets in code, docs, prompts, logs, fixtures, or test snapshots.
- Never print full environment variables.
- Redact tokens, keys, auth headers, cookies, and private key material before logging.
- Do not add production secrets, payment access, deploy credentials, or `docker.sock` access.
- Do not require root for normal worker operation.
- Dangerous shell actions must be blocked or require approval.
- The orchestrator must never merge into `main`.

## Git And File Rules

- Work through branches and PRs.
- Phase work must happen in a branch that clearly corresponds to the active roadmap phase or approved phase slice.
- Do not perform phase work directly on `main`.
- After completing an implementation slice for the active phase, create a commit and push the branch so the work is reviewable.
- If a full roadmap phase is considered complete, merge to `main` happens only after human approval and with a clear summary of what was implemented, verified, and left open.
- Do not rewrite unrelated files.
- Do not do opportunistic refactoring.
- Do not reformat the whole repository unless the task is specifically about formatting.
- Do not commit generated runtime logs, local SQLite databases, CLI auth state, or `.env` files.
- Add `.gitignore` entries before creating local runtime artifacts.

## Testing Expectations

Prefer test coverage around:

- SQLite schema and migrations
- task state transitions
- branch slug generation
- command allowlist and blocklist
- secret redaction
- fake Claude and Codex runners
- fake GitHub client
- temporary git repo integration for worktree creation

Default verification commands:

```bash
python -m compileall src tests
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

If checks cannot run because the project is not yet bootstrapped, state that explicitly and provide manual verification steps.

## Documentation Rules

- Update docs when behavior, architecture, security policy, state machine, CLI commands, config, or workflow changes.
- Keep MVP and future expansion separate.
- Put future-only ideas in `docs/15_FUTURE_EXPANSION.md`.

Canonical supporting documents:

- Task states: `docs/09_TASK_STATES.md`
- Logging: `docs/10_LOGGING_AND_OBSERVABILITY.md`
- CI and review gates: `docs/11_CI_AND_REVIEW_GATES.md`
- Acceptance criteria: `docs/13_MVP_ACCEPTANCE_CRITERIA.md`

## Related Documents

- `docs/development/CODEX_TEAM_MODEL.md`
- `docs/development/SKILL_SCOPE_POLICY.md`
- `docs/runtime/RUNTIME_AGENT_POLICY.md`
