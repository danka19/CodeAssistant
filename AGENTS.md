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

## Non-Negotiable Rules

- Keep changes inside the active roadmap phase.
- Work on each roadmap phase in a corresponding branch for that phase, not on `main`.
- If a request conflicts with `docs/16_MVP_DECISIONS.md`, stop and surface the conflict.
- Do not collapse runtime roles into one vague implementation path.
- Do not introduce auto-merge, auto-deploy, Kubernetes, broad platform scope, or unrelated refactors.
- Never store or print secrets.
- Work through branches and PRs, never direct merge logic into `main`.
- After completing work for a phase slice, create a commit and push the branch.
- If a full phase is complete, prepare a merge to `main` only after human согласование and with a clear description of what was done.
- Update documentation when behavior, policy, workflow, or architecture changes.

## Default Checks

When code changes, run:

```bash
python -m compileall src tests
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

If checks cannot run, say so explicitly and provide manual verification steps.

## Done Criteria

The task is done only when:

- the change matches the active roadmap phase;
- changed files are scoped and explainable;
- checks ran, or the gap is documented honestly;
- docs were updated if behavior or policy changed;
- the final summary states what changed, how it was verified, and what remains open.
