# 08 GitHub Flow

## Core Rules

- `main` is protected.
- Direct push to `main` is forbidden.
- All changes go through feature branches.
- Branch pattern: `agent/task-123-short-slug`.
- Every result is represented as a Pull Request.
- CI checks are required.
- Merge is always manual.
- CodeRabbit is optional.

## Branch Naming

Format:

```text
agent/task-123-short-slug
```

Requirements:

- `task-123` matches the task id in SQLite.
- `short-slug` is derived from the task and must not contain secrets.
- High-risk tasks can use label `risk-high`; they do not need a special branch name.

## Labels

Recommended labels:

- `agent-task`
- `agent-planning`
- `agent-implementing`
- `agent-review`
- `agent-needs-fix`
- `agent-ready-for-human`
- `agent-failed`
- `risk-low`
- `risk-medium`
- `risk-high`

## PR Lifecycle

1. Worker creates PR after commit/push.
2. PR receives labels `agent-task` and a risk label.
3. CI starts automatically.
4. Claude review creates `review.md` and may leave a PR comment.
5. CodeRabbit review works as an optional layer.
6. If blockers exist, PR receives `agent-needs-fix`.
7. After fix and successful checks, PR receives `agent-ready-for-human`.
8. Human decides and merges manually.

## PR Template

```markdown
## Goal

What this task is trying to change.

## Plan

Link or summary from runs/task-123/plan.md.

## Changed Files

- file paths and short explanations

## Tests

- automated checks run
- CI status

## Documentation

- docs/changelog updates
- not needed because ...

## Risks

- known risks
- rollback notes if relevant

## Manual Verification

- steps when automated tests are missing or insufficient

## AI Review Summary

- Claude review result
- CodeRabbit result if enabled
- blockers fixed or remaining notes
```

## Protected Main Settings

Minimum:

- Require pull request before merging.
- Require status checks to pass.
- Require conversation resolution.
- Disallow force pushes.
- Disallow deletions.
- Restrict direct pushes for the agent token.

## What Not To Do In The MVP

- Auto-merge.
- Release automation.
- Deploy from PR.
- Branch protection changes by worker.
- Complex merge queue.
