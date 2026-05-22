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
4. Return `AgentResult`.

## Required Result

```text
AgentResult
status:
summary:
files_read:
files_changed:
checks_run:
findings:
risks:
handoff_notes:
needs_user_decision:
```

## Block Instead Of Guessing

Return `blocked` when:
- the fix requires unassigned files;
- local patterns conflict;
- product/UX/architecture meaning is unclear;
- tests require network or unsafe setup;
- dirty worktree changes make ownership unclear.
