---
name: task-router
description: "Classify ambiguous development requests before broad reading or delegation. Use when Codex must decide task type, minimum context, risk level, whether to keep work local, and which project subagents to use: analyst_architect, programmer, reviewer, or verifier. Do not use for clearly scoped small edits, direct answers, or tasks where the user already specified the exact file and action."
---

# Task Router

Classify before reading broadly.

Use this skill as the default procedural home for:

- ambiguous development requests;
- `continue by plan`, `keep going`, or `what is next`;
- choosing between product roadmap work and documentation/support-track work;
- deciding whether to keep work local or delegate.

Do not use this skill as the source of truth for repo policy. Canonical roadmap authority still lives in `AGENTS.md` and `docs/development/DEVELOPMENT_AGENT_POLICY.md`.

## Output

Return this compact shape:

```text
TaskRoute
task_type:
risk_level:
delegate: yes | no
roles:
minimum_read:
write_set_guess:
checks_guess:
stop_conditions:
reasoning:
```

## Task Types

Use one:
- `direct-answer`: explain or answer without repo edits.
- `small-edit`: simple local change, usually no subagent.
- `implementation`: code or docs change.
- `architecture-investigation`: needs read-only mapping before edits.
- `review`: inspect diff/work and report findings.
- `verification`: run deterministic checks.
- `process-config`: update team, skills, agents, or workflow policy.

## Delegation Defaults

- Prefer no delegation for trivial single-file work.
- Prefer `analyst_architect` before implementation when ownership or architecture is unclear.
- Prefer one `programmer` per write set.
- Prefer `reviewer` after non-trivial changes.
- Prefer `verifier` for deterministic checks.
- Do not load unrelated docs or old project-specific skills.

## Continue-By-Plan Procedure

When the user asks to continue work by plan:

1. Classify the task domain:
   - product implementation; or
   - documentation/support-track work.
2. For product work, treat `docs/12_IMPLEMENTATION_ROADMAP.md` as the canonical roadmap.
3. Read the minimum source-of-truth context:
   - `docs/12_IMPLEMENTATION_ROADMAP.md`
   - `docs/plans/PLAN_INDEX.md`
   - `docs/16_MVP_DECISIONS.md`
   - `docs/state/CURRENT_STATE.md`
4. Read `docs/logs/TASK_LOG.md` as historical evidence about recently completed slices, not as source of truth for current policy or current state.
5. If the task domain is documentation/support-track work, use `docs/plans/PLAN_INDEX.md` to locate the matching support-track plan and then read that plan before routing work.
6. Identify the current unfinished phase or current unfinished plan slice in the matching track.
7. Route to that slice; do not silently pull work from the next phase or from another track.
8. If another plan document is active, use it only if it matches the same task domain.
9. If summary docs conflict with the canonical roadmap for product work, report the conflict and follow the canonical roadmap.

Minimum interpretation rule:

- product implementation routing starts from `docs/12_IMPLEMENTATION_ROADMAP.md`;
- support-track routing starts from `docs/plans/PLAN_INDEX.md` and then the matching support-track plan.

Interpretation defaults:

- do not choose the highest-numbered phase by default;
- do not switch into documentation/governance work unless the task is explicitly about that domain;
- if the request is still ambiguous after minimal reading, return a `TaskRoute` with a stop condition instead of guessing.

## Risk Levels

- `low`: direct answer, docs wording, simple config.
- `medium`: implementation with localized tests or multiple files.
- `high`: architecture, data contracts, security, migrations, external effects, or ambiguous product decisions.

## Stop Conditions

Always include a stop condition when:
- task scope is unclear;
- required write set is not knowable yet;
- user intent conflicts with local docs;
- implementation would require a product, UX, architecture, or data-contract decision.
