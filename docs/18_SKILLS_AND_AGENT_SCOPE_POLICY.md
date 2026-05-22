# Skills and Agent Scope Policy

Version: v1.0
Status: active
Last updated: 2026-05-22

---

## 0. Purpose

This document prevents skills and custom agents from leaking between unrelated projects.

Project-specific skills and subagents must live inside the project that owns them. Global skills and agents are allowed only when they are genuinely reusable across projects.

---

## 1. Storage Rules

Use these locations:

| Type | Location | Rule |
| --- | --- | --- |
| Project skills | `.agents/skills/<skill-name>/SKILL.md` | Preferred for this project |
| Project subagents | `.codex/agents/<agent-name>.toml` | Preferred for this project |
| Project Codex config | `.codex/config.toml` | Stores local agent limits |
| Global reusable skills | `%USERPROFILE%\.codex\skills` | Only for general-purpose, project-agnostic skills |
| Global reusable agents | `%USERPROFILE%\.codex\agents` | Only for general-purpose, project-agnostic agents |

Do not place project-specific workflow, domain, roadmap, build, validation, or handoff skills in global locations.

---

## 2. Current Decision

The old Stamp Room skills are project-specific and must not remain globally active for unrelated projects:
- `router`
- `ops-audit`
- `pxx-executor`
- `dxx-executor`
- `schema-guardian`
- `godot-gate`
- `content-preflight`
- `handoff`
- `doc-sync`
- `ui-boundary`

These names and workflows belong to Stamp Room's docs, Godot gates, PXX/DXX roadmaps, and task-state conventions.

For this project, use a new local minimal skill set instead:
- `task-router`
- `team-handoff`
- `implementation-protocol`
- `review-protocol`
- `verification-gate`

---

## 3. Skill Selection Rules

Skills are procedural context. They are not a role system.

Good skills:
- describe repeatable project procedure;
- are short;
- include sharp trigger language;
- avoid broad domain dumps;
- load references only when needed.

Bad skills:
- duplicate general model knowledge;
- encode another project's roadmap or terminology;
- trigger implicitly for too many tasks;
- combine planning, writing, review, and close-out in one file.

---

## 4. Local Skill Set

## 4.1 `task-router`

Use when the request is ambiguous and the assistant must decide:
- task type;
- whether subagents are useful;
- minimum context to read;
- risks and stop conditions.

Do not use for clearly scoped small edits.

## 4.2 `team-handoff`

Use when creating or consuming delegated work:
- `TaskBrief`
- `WorkOrder`
- `AgentResult`
- `ReviewReport`

This is the core skill for keeping context compact.

## 4.3 `implementation-protocol`

Use when code or docs will be edited.

It enforces:
- one write set;
- no hidden scope expansion;
- concise result reporting;
- explicit checks.

## 4.4 `review-protocol`

Use when reviewing a diff or completed work.

It enforces:
- findings first;
- severity;
- file/line references;
- no edits by the reviewer.

## 4.5 `verification-gate`

Use when running deterministic checks:
- tests;
- build;
- lint;
- typecheck;
- smoke commands.

It should contain project-specific commands once the stack is known.

---

## 5. Global Skill Policy

Keep globally only:
- official/system skills;
- broadly useful personal skills that do not mention a specific project;
- generic file-format skills;
- generic API/platform documentation skills.

Move or delete globally installed project-specific skills.

Before deleting a global project-specific skill:
1. confirm that a project-local copy exists in the owning project;
2. confirm it is not the only copy;
3. remove the global copy;
4. document the owning project location.

---

## 6. Model and Cost Policy

Subagent model choice must be explicit.

Default principle:
- cheap/read-only model for exploration and verification;
- coding-optimized model for implementation;
- stronger reasoning model for review;
- frontier/highest-cost model only after a stated escalation reason.

Do not pay 5x cost for a routine 1% accuracy gain unless the task is high-risk enough to justify it.

`gpt-5.5` is reserved for explicit escalation only.

Allowed escalation reasons:
- high-impact architecture decision;
- security-sensitive change;
- data-loss or irreversible-state risk;
- conflicting source-of-truth docs or review findings;
- repeated failure on cheaper models;
- a decision that materially constrains future system design.

Disallowed escalation reasons:
- routine implementation;
- docs-only changes;
- low-risk planning;
- ordinary test or lint failures;
- broad repository discovery;
- marginal quality preference without concrete risk.

---

## 7. Migration Plan

1. Keep this project's team skills in `.agents/skills`.
2. Keep this project's subagents in `.codex/agents`.
3. Remove Stamp Room-specific skills from `%USERPROFILE%\.codex\skills` after confirming Stamp Room has local copies.
4. If Stamp Room needs current Codex repo-skill discovery, migrate its `.codex/skills` tree to `.agents/skills` inside Stamp Room in a separate Stamp Room-scoped change.
5. Do not copy Stamp Room skills into this project.
