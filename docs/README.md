# Documentation Map

Status: active
Audience: humans and coding agents
Owner: repository maintainers
Update when: adding, moving, splitting, or deprecating documentation

## Purpose

This directory is the source of truth for product, workflow, runtime, and development documentation for the AI Dev Orchestrator project.

The documentation system is optimized for agent work:

- one topic per file;
- short entrypoints and deep links instead of one long omnibus document;
- stable semantic folders for policy documents;
- explicit source-of-truth mapping;
- clear separation between development-time policy and future runtime behavior.

## Top-Level Layout

- `docs/README.md`: documentation index and source-of-truth map.
- `docs/governance/`: documentation standards, maintenance rules, and refactor plans.
- `docs/development/`: development-time policy for contributors and Codex collaboration in this repository.
- `docs/runtime/`: behavior and guardrails for the future orchestrated agents running on the VPS.
- `docs/00_*.md` through `docs/16_*.md`: product, architecture, workflow, and MVP records that already define the system being built.

## Source Of Truth Map

- Project purpose and high-level story: `docs/00_PROJECT_OVERVIEW.md`
- MVP scope: `docs/01_MVP_SCOPE.md`
- Architecture: `docs/02_ARCHITECTURE.md`
- End-to-end workflow: `docs/03_WORKFLOW.md`
- Security model: `docs/04_SECURITY_MODEL.md`
- Runtime role overview: `docs/05_AGENT_ROLES.md`
- Worker environment: `docs/07_VPS_WORKER_SPEC.md`
- Task states: `docs/09_TASK_STATES.md`
- Logging and observability: `docs/10_LOGGING_AND_OBSERVABILITY.md`
- CI and review gates: `docs/11_CI_AND_REVIEW_GATES.md`
- Implementation phases: `docs/12_IMPLEMENTATION_ROADMAP.md`
- MVP acceptance criteria: `docs/13_MVP_ACCEPTANCE_CRITERIA.md`
- Future-only ideas: `docs/15_FUTURE_EXPANSION.md`
- Active MVP decisions: `docs/16_MVP_DECISIONS.md`
- Product knowledge-system model: `docs/19_AGENT_KNOWLEDGE_SYSTEM.md`
- Documentation operating rules: `docs/20_DOCUMENTATION_OPERATIONS.md`
- Current repository pilot plan: `docs/21_PILOT_KNOWLEDGE_SYSTEM_PLAN.md`
- Documentation rules and structure: `docs/governance/DOCUMENTATION_STANDARD.md`
- Documentation refactor backlog: `docs/governance/DOCS_REFACTOR_PLAN.md`
- Development-time repository policy: `docs/development/DEVELOPMENT_AGENT_POLICY.md`
- Codex local team model: `docs/development/CODEX_TEAM_MODEL.md`
- Project-local skill policy: `docs/development/SKILL_SCOPE_POLICY.md`
- Runtime policy entrypoint: `docs/runtime/RUNTIME_AGENT_POLICY.md`

## Naming Rules

- New governance and policy files use semantic names, not numeric prefixes.
- Product-level numbered docs remain valid for platform decisions and rollout planning.
- New files should describe exactly one concern.
- Use uppercase snake case for policy and standard files, for example `RUNTIME_AGENT_POLICY.md`.
- Keep filenames stable. Prefer updating content over renaming unless the topic split is real.

## Maintenance Rules

- Do not add new long mixed-topic policy documents.
- If a file starts covering more than one operational concern, split it.
- Keep entrypoint files short and link to detailed source documents.
- When behavior changes, update the source-of-truth file first and then any summaries.

For detailed standards, see `docs/governance/DOCUMENTATION_STANDARD.md`.
