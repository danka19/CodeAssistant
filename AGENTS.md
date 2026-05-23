# AGENTS.md

Development-time entrypoint for agents working on this repository.

This file is intentionally short. Detailed policy lives in `docs/`.

## What This Repository Is

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

The project must stay GitHub-first, small, auditable, and deployable on a single rented VPS.

## Read First

Before implementing, use these source documents:

- docs map: `docs/README.md`
- MVP scope: `docs/01_MVP_SCOPE.md`
- architecture: `docs/02_ARCHITECTURE.md`
- workflow: `docs/03_WORKFLOW.md`
- security model: `docs/04_SECURITY_MODEL.md`
- worker environment: `docs/07_VPS_WORKER_SPEC.md`
- roadmap phase: `docs/12_IMPLEMENTATION_ROADMAP.md`
- active decisions: `docs/16_MVP_DECISIONS.md`
- detailed repository policy: `docs/development/DEVELOPMENT_AGENT_POLICY.md`
- Codex team model: `docs/development/CODEX_TEAM_MODEL.md`
- skill policy: `docs/development/SKILL_SCOPE_POLICY.md`
- runtime policy entrypoint: `docs/runtime/RUNTIME_AGENT_POLICY.md`

## How To Read Roadmaps And Phases

This section is a summary. Canonical detailed interpretation rules live in `docs/development/DEVELOPMENT_AGENT_POLICY.md`, and the procedural routing algorithm lives in project-local skill `task-router`.

- Treat `docs/12_IMPLEMENTATION_ROADMAP.md` as the canonical product roadmap.
- Treat product phases in `docs/12_IMPLEMENTATION_ROADMAP.md` as the default implementation track unless the user explicitly asks for a documentation or governance task.
- Use `docs/plans/PLAN_INDEX.md` only as a router to plan documents, not as permission to switch tracks on your own.
- Use `docs/state/CURRENT_STATE.md` to understand what is true now, not to override the canonical product roadmap.
- Distinguish product phases from support tracks:
  - product implementation phases govern MVP feature delivery;
  - documentation, governance, or knowledge-system plans govern repository-structure work only when the task is explicitly about those topics.
- If multiple plan documents are active at the same time, choose the one that matches the user's requested work instead of following the most recently updated plan document.
- If `CURRENT_STATE.md`, `PLAN_INDEX.md`, or another summary document appears to conflict with `docs/12_IMPLEMENTATION_ROADMAP.md`, treat `docs/12_IMPLEMENTATION_ROADMAP.md` as authoritative for product implementation and report the conflict.
- For the procedural algorithm behind `continue by plan`, use project-local skill `task-router`.
- Before file edits, use project-local skill `implementation-protocol`.
- For delegated work contracts and typed subagent outputs, use project-local skill `team-handoff`.
- For deterministic checks and evidence gathering, use project-local skill `verification-gate`.
- For findings-first read-only review, use project-local skill `review-protocol`.

## Non-Negotiable Rules

- Keep changes inside the active work track that matches the task domain:
  - product implementation -> the active product phase in `docs/12_IMPLEMENTATION_ROADMAP.md`;
  - documentation/support work -> the active matching support-track plan.
- Do not jump from a product phase to a documentation/support track unless the task is explicitly about documentation architecture, governance, or knowledge-system rollout.
- If a request conflicts with `docs/16_MVP_DECISIONS.md`, stop and surface the conflict.
- Do not collapse runtime roles into one vague implementation path.
- Do not introduce auto-merge, auto-deploy, Kubernetes, broad platform scope, or unrelated refactors.
- Never store or print secrets.
- Work through branches and PRs, never direct merge logic into `main`.
- Update documentation when behavior, policy, workflow, or architecture changes.

## Default Checks

The canonical default checks for code changes are defined in `docs/development/DEVELOPMENT_AGENT_POLICY.md`.

When running or narrowing verification, use project-local skill `verification-gate`.

Default commands:

```bash
python -m compileall src tests
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

If checks cannot run, say so explicitly and provide manual verification steps.

## Done Criteria

The task is done only when:

- the change matches the active work track for the task domain;
- changed files are scoped and explainable;
- checks ran, or the gap is documented honestly;
- docs were updated if behavior or policy changed;
- the final summary states what changed, how it was verified, and what remains open.
