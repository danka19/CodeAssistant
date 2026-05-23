---
name: implementation-protocol
description: "Constrain code or documentation edits to a clear write set. Use when Codex or the programmer subagent will modify project files, apply patches, create configs, or update docs. Do not use for read-only analysis, review-only work, or pure command verification."
---

# Implementation Protocol

Before editing:
- identify the write set;
- check nearby patterns;
- name non-goals;
- avoid unrelated cleanup.

During editing:
- make the smallest defensible change;
- stay inside assigned files;
- do not invent architecture or product decisions;
- stop if required work crosses ownership boundaries.

Use this skill as the procedural home for:

- preparing a write set;
- executing scoped edits;
- task close-out mechanics after implementation.

Do not duplicate repo-wide policy here. Canonical documentation-update responsibility remains in `docs/20_DOCUMENTATION_OPERATIONS.md`.

## Write-Set Rules

Allowed write sets:
- exact files;
- narrow directories;
- generated files explicitly requested by the parent.

Never edit:
- unrelated formatting;
- old project-specific skills;
- user changes outside scope;
- files outside `write_paths` without parent approval.

## Edit Workflow

1. Read the minimum local context needed.
2. Apply the smallest patch.
3. Run targeted formatting or checks only when relevant.
4. Return the typed `AgentResult` shape defined in project-local skill `team-handoff`.

## Close-Out Checklist

After implementation work:

1. Check whether behavior, workflow, architecture, state, config, policy, or operator procedure changed.
2. If yes, update the canonical doc for that topic in the same task.
3. Add a task log entry in `docs/logs/TASK_LOG.md` for completed repository-level task work.
4. If current factual repo status changed, update `docs/state/CURRENT_STATE.md`.
5. If a durable decision was made, update the relevant decision document.
6. Run the relevant checks or report honestly why they were not run.

For the canonical documentation rules and evidence model, consult `docs/20_DOCUMENTATION_OPERATIONS.md` instead of restating it here.

## Block Instead Of Guessing

Return `blocked` when:
- the fix requires unassigned files;
- local patterns conflict;
- product/UX/architecture meaning is unclear;
- tests require network or unsafe setup;
- dirty worktree changes make ownership unclear.
