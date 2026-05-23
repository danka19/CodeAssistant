# Documentation Refactor Plan

Status: active
Audience: maintainers
Owner: repository maintainers
Update when: documentation architecture or migration status changes

## Objective

Bring the repository documentation to a maintainable state for AI-agent collaboration by reducing duplicated policy, shortening entrypoints, and decomposing mixed-topic documents.

## Problems Found

- `AGENTS.md` mixed repository entrypoint rules with detailed Codex team policy.
- `docs/AGENTS_FOR_VPS.md` mixed runtime overview, role contracts, logging, security, limits, and done criteria.
- `docs/17_CODEX_TEAM_KIT.md` and `docs/18_SKILLS_AND_AGENT_SCOPE_POLICY.md` were detailed but disconnected from a broader docs map.
- The `docs/` root had no index, no folder taxonomy, and no documented source-of-truth map.
- New policy documents had no stable semantic location.

## Target State

- `AGENTS.md` becomes short and high-signal.
- `docs/README.md` becomes the entrypoint for the docs tree.
- Development-time policy lives under `docs/development/`.
- Runtime policy lives under `docs/runtime/`.
- Documentation rules live under `docs/governance/`.
- Old mixed files remain as compatibility entrypoints or are replaced by stubs.

## Refactor Steps

1. Create a docs index and documentation standard.
2. Move development-time detail out of `AGENTS.md`.
3. Split runtime policy into overview, role contracts, and logging/security/limits.
4. Convert old mixed policy files into short navigational stubs.
5. Keep numbered product and architecture docs as canonical system-design records for now.
6. In a later pass, split `docs/16_MVP_DECISIONS.md` into ADR-style files if decision churn increases.

## This Pass

Completed in this refactor:

- added `docs/README.md`;
- added `docs/governance/DOCUMENTATION_STANDARD.md`;
- added `docs/development/DEVELOPMENT_AGENT_POLICY.md`;
- added `docs/development/CODEX_TEAM_MODEL.md`;
- added `docs/development/SKILL_SCOPE_POLICY.md`;
- added `docs/runtime/` policy documents;
- shortened `AGENTS.md`;
- converted legacy policy-heavy docs into short link documents.

Not done in this pass:

- full ADR migration for `docs/16_MVP_DECISIONS.md`;
- relocating the numbered system/spec docs into semantic folders;
- unifying legacy language and encoding across all earlier numbered documents.
