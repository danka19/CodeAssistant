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

Always identify the active work track before implementing:

- for product implementation, identify the current phase in `docs/12_IMPLEMENTATION_ROADMAP.md`;
- for documentation/support work, identify the matching support-track plan routed by `docs/plans/PLAN_INDEX.md`.

If a request conflicts with `docs/16_MVP_DECISIONS.md`, stop and surface the conflict.

## Roadmap Interpretation Rules

Use the documentation architecture deliberately:

- `docs/12_IMPLEMENTATION_ROADMAP.md` is the canonical roadmap for product implementation.
- `docs/plans/PLAN_INDEX.md` is a routing document that points to plan sources; it does not by itself choose the track you should work on.
- `docs/state/CURRENT_STATE.md` is a factual status document; use it to understand what is currently true, but do not let it override the canonical product roadmap.
- Numbered product phases in `docs/12_IMPLEMENTATION_ROADMAP.md` should be treated as product-delivery phases unless a phase explicitly states otherwise.
- Do not treat a minimal vertical slice or bootstrap increment as completion of a roadmap phase unless the remaining implementation items and readiness criteria for that phase are satisfied.
- Documentation, governance, migration, and knowledge-system plans are support tracks. They become the active work track only when:
  - the user explicitly asks for documentation/governance work; or
  - the current implementation task is itself about documentation architecture or repository policy.
- When both a product roadmap and a documentation/support plan are active, prefer the product roadmap for feature implementation and prefer the support plan for documentation-structure work.
- Do not infer that the highest-numbered phase is the next product step. Match the phase to the work domain instead.
- If a summary document, status note, or secondary plan appears to conflict with `docs/12_IMPLEMENTATION_ROADMAP.md`, treat `docs/12_IMPLEMENTATION_ROADMAP.md` as authoritative for product implementation and surface the discrepancy in your summary.
- Prefer multi-agent execution when the work benefits from separation of analysis, implementation, verification, or review responsibilities.
- A single assistant may complete the task locally only when the change is genuinely small, does not involve important decisions, and has low realistic risk of coding error.
- The detailed procedure for `continue by plan` lives in project-local skill `task-router`.
- The detailed close-out procedure for implementation work lives in project-local skill `implementation-protocol`.
- The detailed verification procedure lives in project-local skill `verification-gate`.
- The detailed delegation contract and typed result procedure lives in project-local skill `team-handoff`.
- The detailed findings-first review procedure lives in project-local skill `review-protocol`.

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
- Use the project-local skill `implementation-protocol` when preparing scoped edits and close-out work.
- Before starting implementation work, run a repository sync step:
  - fetch the remote repository;
  - update local `main` from `origin/main`;
  - confirm that the branch point for new work is the updated `main`.
- Phase work must happen in a branch that clearly corresponds to the active roadmap phase or approved phase slice.
- Create the working branch only after the sync step succeeds.
- Do not perform phase work directly on `main`.
- Name the working branch so the active phase is obvious from the branch name.
- If local `main` cannot be updated safely, stop and get human agreement before branching or editing phase work.
- After completing an implementation slice for the active phase, create a commit and push the branch so the work is reviewable.
- Do not declare a roadmap phase complete just because one useful slice works locally; phase completion requires satisfying that phase's stated implementation scope and readiness criteria in `docs/12_IMPLEMENTATION_ROADMAP.md`.
- If a full roadmap phase is considered complete, merge to `main` happens only after human approval and with a clear summary of what was implemented, verified, and left open.
- Do not rewrite unrelated files.
- Do not do opportunistic refactoring.
- Do not reformat the whole repository unless the task is specifically about formatting.
- Do not commit generated runtime logs, local SQLite databases, CLI auth state, or `.env` files.
- Add `.gitignore` entries before creating local runtime artifacts.
- If environment restrictions block meaningful implementation, verification, or live smoke testing, first determine the specific boundary, then stop and get human agreement on how to adjust the environment. Do not quietly accept the reduced environment as "good enough" when it prevents proper completion of the requested work.

## Testing Expectations

Use project-local skill `verification-gate` for the operational procedure around choosing and reporting checks.

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

Do not treat dry verification as sufficient for user-visible or runtime-facing changes when a realistic smoke path is available in the current environment. Before claiming the work is ready in those cases:

- run the closest practical live smoke test for the changed path;
- prefer exercising the real entrypoint over only calling internal functions;
- state exactly what was run and what behavior was observed;
- if the live smoke path is blocked by missing credentials, unavailable services, or environment limits, say that explicitly and do not imply readiness beyond the dry checks.
- if the block matters to completing the requested work, stop and agree with the user on the needed environment setup instead of continuing as though the missing capability were acceptable.

## Documentation Rules

- Update docs when behavior, architecture, security policy, state machine, CLI commands, config, or workflow changes.
- Keep MVP and future expansion separate.
- Put future-only ideas in `docs/15_FUTURE_EXPANSION.md`.
- Use project-local skill `implementation-protocol` for the operational close-out checklist that applies these rules.
- If branch-start procedure changes, update both `AGENTS.md` and this policy document together.
- When documenting roadmap status, explicitly say whether you mean:
  - active product phase; or
  - active documentation/support track.
- Avoid using the phrase `active phase` without the domain qualifier if more than one planning track exists.

Canonical supporting documents:

- Task states: `docs/09_TASK_STATES.md`
- Logging: `docs/10_LOGGING_AND_OBSERVABILITY.md`
- CI and review gates: `docs/11_CI_AND_REVIEW_GATES.md`
- Acceptance criteria: `docs/13_MVP_ACCEPTANCE_CRITERIA.md`

## Related Documents

- `docs/development/CODEX_TEAM_MODEL.md`
- `docs/development/SKILL_SCOPE_POLICY.md`
- `docs/runtime/RUNTIME_AGENT_POLICY.md`
