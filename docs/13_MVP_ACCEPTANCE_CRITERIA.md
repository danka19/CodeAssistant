# 13 MVP Acceptance Criteria

The MVP is ready when all criteria below are met.

## End-To-End Criteria

- I can send `/task` in Telegram.
- The system creates a task in the database.
- The system assigns `task_id`.
- The system creates a branch.
- The system creates a git worktree.
- Claude creates `plan.md`.
- Large tasks have approval before implementation.
- Codex makes a change in the test repository.
- The system runs configured checks or explicitly states that automated checks are unavailable.
- The system creates a PR.
- Telegram sends the PR link.
- Main is protected from direct merge.
- Logs are available in `/runs/task-123`.
- On failure, the task receives `failed` and a clear reason.
- Merge remains manual.

## Documentation Criteria

- `AGENTS.md` exists.
- Telegram bot is documented.
- VPS worker is documented.
- GitHub PR flow is documented.
- Claude/Codex/CodeRabbit/Human roles are documented.
- Security gates are documented.
- Task states are documented.
- Logs are documented.
- CI/review gates are documented.
- Risks and limitations are documented.

## Security Criteria

- Worker does not run as root.
- Agent token cannot push to `main`.
- Secrets do not enter git.
- Secrets do not enter logs.
- Dangerous commands require approval or are blocked.
- Production deploy and payments are absent from the MVP.

## Failure Criteria

The MVP must correctly handle:

- GitHub auth failure;
- Claude failure;
- Codex failure;
- test failure;
- PR creation failure;
- cancellation;
- missing CI;
- no tests configured.

Correct handling means: task status is updated, reason is recorded, and the user receives a Telegram notification.
