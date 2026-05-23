# Runtime Agent Policy

Status: active
Audience: future runtime agents and maintainers
Owner: repository maintainers
Update when: runtime workflow, boundaries, or orchestration policy changes

## Purpose

This is the runtime entrypoint for the future agents that will run inside the AI Dev Orchestrator on the VPS.

It is not the development-time policy for this repository. For repository contribution rules, use `AGENTS.md` and `docs/development/DEVELOPMENT_AGENT_POLICY.md`.

## Core Principle

Runtime agents may help prepare work for review, but they do not own the final merge decision.

GitHub remains the source of truth for code, branches, PRs, CI, and merge state. Telegram is the human-facing control surface for intake, status, and approvals.

## MVP Runtime Chain

```text
Telegram user
-> Intake Assistant
-> task_brief.yaml
-> Claude Planner
-> optional human approval
-> Codex Implementer
-> build/test/lint
-> Pull Request
-> Claude Reviewer
-> optional fix loop
-> ready for Human
```

This is a sequential pipeline, not a free-form multi-agent swarm.

## Runtime Source Documents

- Runtime role boundaries: `docs/runtime/RUNTIME_ROLE_CONTRACTS.md`
- Runtime logging and security: `docs/runtime/RUNTIME_LOGGING_AND_SECURITY.md`
- Runtime limits and done criteria: `docs/runtime/RUNTIME_LIMITS_AND_DONE_CRITERIA.md`
- Runtime role overview: `docs/05_AGENT_ROLES.md`
- Task states: `docs/09_TASK_STATES.md`
- Logging model: `docs/10_LOGGING_AND_OBSERVABILITY.md`
- CI and review gates: `docs/11_CI_AND_REVIEW_GATES.md`
- Active MVP decisions: `docs/16_MVP_DECISIONS.md`
