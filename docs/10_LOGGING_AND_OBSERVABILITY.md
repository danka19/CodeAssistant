# 10 Logging And Observability

## Per-Task Files

For each task, save:

```text
/runs/task-123/input.md
/runs/task-123/plan.md
/runs/task-123/implementation.log
/runs/task-123/test.log
/runs/task-123/review.md
/runs/task-123/fix.log
/runs/task-123/summary.md
/runs/task-123/events.jsonl
```

For large/risky tasks, also save:

```text
/runs/task-123/architecture_plan.md
/runs/task-123/approval.md
```

## What To Write To Logs

- task_id, repo, branch, worktree path;
- timestamps;
- state transitions;
- high-level commands;
- exit codes;
- sanitized stdout/stderr;
- PR and CI links;
- check results;
- review blockers;
- manual verification steps.

## What Not To Write To Logs

- tokens;
- auth headers;
- cookies;
- full environment dump;
- private keys;
- production secrets;
- payment data;
- contents of files unrelated to the task;
- personal user data unless necessary.

## Redaction

Before writing logs, the worker must apply redaction for:

- env variable values with names containing `TOKEN`, `SECRET`, `KEY`, `PASSWORD`;
- GitHub tokens;
- Telegram bot token;
- Anthropic/OpenAI auth;
- SSH private key blocks;
- URLs with credentials.

## How To Inspect Status

- Telegram: `/status task-123`.
- Telegram: `/log task-123`.
- VPS: open `/runs/task-123/events.jsonl`.
- GitHub: PR checks and comments.
- SQLite: task row and events.

## How To Debug A Failed Task

1. Check `/runs/task-123/events.jsonl`.
2. Find `failed_step`.
3. Check the corresponding log: planning, implementation, test, review.
4. Check `git status` in the worktree.
5. Check PR and CI if PR already exists.
6. Decide: manual retry, new task, close PR, request approval.

## How To Replay A Task Manually

Minimal manual replay:

1. Go to the task worktree.
2. Check branch.
3. Read `input.md` and `plan.md`.
4. Run check commands from `test.log` or config.
5. Run Codex manually with the same plan if needed.
6. Commit/push manually.
7. Update PR.

## MVP Observability

The MVP does not need Prometheus, Grafana, or distributed tracing. SQLite state, `events.jsonl`, file logs, and Telegram notifications are enough.

Later, add metrics endpoint, retention policy, alerting, and dashboard.
