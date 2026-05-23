# 09 Task States

This document records the full MVP target state machine.

Current implementation status:

- Phase 1 persists the intake subset: `queued` and `failed`.
- The current Phase 2 operator bridge can transition a queued task to `planning` after branch/worktree preparation is complete.
- The rest of the workflow states remain planned for later phases.

## State Machine

```text
queued
-> planning
-> waiting_plan_approval
-> implementing
-> testing
-> creating_pr
-> reviewing
-> needs_fix
-> fixing
-> testing
-> reviewing
-> ready_for_human
-> done
```

Terminal states:

```text
done
failed
cancelled
plan_rejected
```

## Statuses

| Status | Meaning | Changed By | Next Statuses | Data |
|---|---|---|---|---|
| `queued` | Task waiting for worker | Bot/Worker | `planning`, `cancelled`, `failed` | task_id, priority, created_at |
| `planning` | Claude prepares plan | Worker | `waiting_plan_approval`, `implementing`, `failed`, `cancelled` | branch, worktree, planning log |
| `waiting_plan_approval` | Approval required | Worker | `implementing`, `plan_rejected`, `cancelled` | plan path, approval request |
| `plan_rejected` | Plan rejected | Bot/Human | terminal | rejection reason |
| `implementing` | Codex implements | Worker | `testing`, `failed`, `cancelled` | implementation log, changed files |
| `testing` | Worker runs checks | Worker | `creating_pr`, `failed`, `reviewing`, `cancelled` | test log, check results |
| `creating_pr` | PR is being created | Worker | `reviewing`, `failed` | branch, commit sha, PR URL |
| `reviewing` | Claude/CI/CodeRabbit review | Worker | `needs_fix`, `ready_for_human`, `failed` | review.md, CI status |
| `needs_fix` | Blockers exist | Review runner | `fixing`, `failed`, `cancelled` | blocker list |
| `fixing` | Codex fixes blockers | Worker | `testing`, `failed`, `cancelled` | fix.log, attempt number |
| `ready_for_human` | Ready for manual review/merge | Worker | `done`, `failed` | PR URL, summary, checks |
| `done` | Human marked finished after merge or decision | Human/Bot | terminal | merge sha or closure note |
| `failed` | Execution failed | Worker | terminal or manual retry | failure reason, failed step |
| `cancelled` | Task cancelled | Bot/Worker | terminal | cancellation reason |

## Transition Rules

- Do not create PR without branch and worktree.
- Do not set `ready_for_human` without PR URL or explicit non-coding result.
- Do not set `done` automatically after PR creation.
- `done` does not mean auto-merge. In the MVP, it is a manual status after a human decision.
- Fix loop must have an attempt limit.

## Current Phase 1 Subset

For the currently implemented intake slice:

- `/task` stores a task in SQLite with status `queued`;
- `/tasks` lists recent tasks and opens per-task status through Telegram buttons;
- `/status` reads the current stored status;
- `/help` returns the available intake commands;
- unauthorized requests are rejected without creating a task;
- the manual `prepare-workspace` CLI bridge can prepare repo/worktree and move a queued task to `planning`;
- Claude planning, approval, implementation, PR, and review transitions still start in later phases.
