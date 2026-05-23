# Current State

Status: active
Audience: humans and coding agents
Owner: repository maintainers
Last reviewed: 2026-05-23

## Purpose

This file is the canonical present-tense status document for the CodeAssistant repository.

Use it to answer:

- what is already true now;
- which documentation architecture is active;
- which roadmap phase is currently relevant;
- which documentation gaps are still open.

Do not use this file for speculative plans or append-only history.

## Current Project Status

- Product direction: AI Dev Orchestrator for a Linux VPS.
- Active product documentation includes MVP scope, architecture, workflow, security, worker spec, roadmap, and MVP decisions.
- Phase 0 repository bootstrap is complete.
- The repository now follows a folder-first layout with code in `src/`, tests in `tests/`, tracked templates in `config/`, and durable instructions in `docs/`.
- The initial minimal implementation for Phase 1 is complete with a runnable Telegram polling intake bot for `/task`, `/tasks`, `/status`, and `/help`, SQLite storage for tasks/events, allowlist checks, and test coverage.
- An initial Phase 2 foundation now exists for repository cache preparation and per-task worktree creation, including branch slug generation, managed-path safety checks, persisted task workspace metadata, and git command event logging.
- Development-time repository policy has been split into `docs/development/`.
- Future runtime agent policy has been split into `docs/runtime/`.
- Governance and documentation rules have been split into `docs/governance/`.
- Product-level knowledge-system policy is now defined in:
  - `docs/19_AGENT_KNOWLEDGE_SYSTEM.md`
  - `docs/20_DOCUMENTATION_OPERATIONS.md`
- Product-level pilot rollout planning is defined in:
  - `docs/21_PILOT_KNOWLEDGE_SYSTEM_PLAN.md`

## Documentation Architecture Status

Implemented:

- top-level docs index: `docs/README.md`
- development policy layer: `docs/development/*`
- runtime policy layer: `docs/runtime/*`
- governance layer: `docs/governance/*`
- compatibility entrypoints for legacy mixed policy docs
- product-level knowledge-system definition
- current-state layer
- task-log layer
- decision index layer
- plan index layer
- architecture, development, and runtime maps

Not yet implemented:

- split of `docs/16_MVP_DECISIONS.md` into smaller decision records
- metadata normalization across all older numbered docs
- systematic cleanup of any remaining encoding issues in older docs
- automated validation for documentation freshness

## Canonical Ownership Snapshot

- top-level docs map: `docs/README.md`
- present-tense repo state: `docs/state/CURRENT_STATE.md`
- task history: `docs/logs/TASK_LOG.md`
- durable decision routing: `docs/decisions/DECISION_INDEX.md`
- active plan routing: `docs/plans/PLAN_INDEX.md`
- development-time contributor rules: `AGENTS.md` and `docs/development/*`
- future runtime agent behavior: `docs/runtime/*`

## Active Roadmap Context

- The repository already has an MVP roadmap in `docs/12_IMPLEMENTATION_ROADMAP.md`.
- `Phase 1 - Telegram Intake` is complete in the repository at the minimal initial implementation level accepted for this branch.
- `Phase 2 - GitHub/Repo Manager` is now in progress with repository/worktree preparation foundations landed; remaining work includes worker wiring and authenticated remote execution in the full runtime flow.
- Product implementation remains governed by Phases 2 through 7 for MVP behavior and worker capabilities.
- The product roadmap contains `Phase 8 - Knowledge System Rollout` as the product-level documentation initiative.
- The operational support-track plan for that initiative is `docs/21_PILOT_KNOWLEDGE_SYSTEM_PLAN.md`, routed via `docs/plans/PLAN_INDEX.md`.
- These are different planning tracks:
  - use the product roadmap for feature and workflow implementation;
  - use the support-track plan routed by `docs/plans/PLAN_INDEX.md` for documentation architecture, governance, or knowledge-system work.
- Do not interpret `Phase 8` as the next default product implementation step or as the operational router for support-track tasks.
- The current repository serves as the pilot proving ground for this model.

## Open Documentation Gaps

- verify whether mojibake seen in some shell output reflects actual file encoding issues or only terminal rendering;
- decide when to split large decision and architecture omnibus files;
- define the first stable rule for metadata normalization on older numbered docs.
- decide when to promote the current intake bot into the fuller Telegram command set described for later phases.
- decide whether `/tasks` needs pagination, filtering, or richer per-task actions once the task list grows.
