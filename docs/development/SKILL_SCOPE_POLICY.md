# Skill Scope Policy

Status: active
Audience: contributors and coding agents
Owner: repository maintainers
Update when: project-local skill inventory or storage policy changes

## Purpose

Prevent project-specific skills, prompts, and agent procedures from leaking across unrelated repositories.

## Storage Rules

Use these locations:

| Type | Location | Rule |
| --- | --- | --- |
| Project skills | `.agents/skills/<skill-name>/SKILL.md` | Preferred for this repository |
| Project subagents | `.codex/agents/<agent-name>.toml` | Preferred for this repository |
| Project Codex config | `.codex/config.toml` | Stores local agent limits |
| Global reusable skills | `%USERPROFILE%\\.codex\\skills` | Only for project-agnostic skills |
| Global reusable agents | `%USERPROFILE%\\.codex\\agents` | Only for project-agnostic agents |

Do not place repository-specific workflow, roadmap, handoff, or validation skills in global locations.

## Allowed Local Skill Set

Use only these project-local skills:

- `task-router`
  Route ambiguous work, `continue by plan`, roadmap-track choice, risk, and delegation.
- `team-handoff`
  Define typed delegation contracts and normalized subagent outputs.
- `implementation-protocol`
  Govern scoped edits and implementation close-out procedure.
- `review-protocol`
  Govern read-only findings-first review procedure.
- `verification-gate`
  Govern deterministic check selection, execution, and reporting.

Do not import Stamp Room-specific skills into this repository.

## Skill Quality Rules

Good skills:

- describe repeatable procedure;
- have clear trigger conditions;
- are short;
- avoid domain dumps;
- load references only when needed.

Bad skills:

- duplicate model-common knowledge;
- encode another project's terminology;
- trigger for too many task types;
- combine planning, implementation, review, and close-out in one skill.

## Model And Cost Principle

- cheap read-only model for exploration and verification;
- coding-optimized model for implementation;
- stronger reasoning model for review;
- frontier model only after explicit escalation.

See `docs/development/CODEX_TEAM_MODEL.md` for the exact role-model policy.
