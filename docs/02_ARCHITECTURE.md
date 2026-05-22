# 02 Architecture

## Overall Flow

```text
Telegram task
-> task queue
-> branch/worktree
-> Claude plan
-> optional approval
-> Codex implementation
-> tests
-> PR
-> review
-> report to Telegram
-> manual merge
```

## Components

### Telegram Bot

- Responsibility: accept user commands and send notifications.
- Inputs: `/task`, `/status`, `/log`, `/approve`, `/reject`, `/cancel`, `/help`.
- Outputs: SQLite records, events, Telegram messages.
- Must not: run shell commands, store secrets in messages, make merge decisions.
- Risks: user spoofing, context loss, overly long messages.
- MVP: one allowed Telegram user id, polling or webhook, minimal commands.
- Later: multiple users, roles, inline buttons, richer status cards.

### API/Worker Process

- Responsibility: main glue layer and state machine.
- Inputs: tasks from SQLite, approvals, cancel events.
- Outputs: git, Claude, Codex, tests, GitHub PR, notifications.
- Must not: bypass security gates or execute unauthorized destructive commands.
- Risks: stuck subprocesses, partial failures, race conditions.
- MVP: one worker loop, task lock while running.
- Later: queue, retries, parallel workers, supervisor.

### SQLite Database

- Responsibility: store task state, approvals, events, paths, and PR metadata.
- Inputs: bot commands and worker events.
- Outputs: state for `/status`, worker loop, and audit.
- Must not: store secrets or full agent prompts containing credentials.
- Risks: corruption from incorrect concurrent writes, no backups.
- MVP: local `/data/tasks.sqlite`, WAL mode, simple migrations.
- Later: PostgreSQL, retention policy, task search.

### GitHub Integration

- Responsibility: push branch, create PR, read CI status, labels, comments.
- Inputs: branch, commit, PR body, labels.
- Outputs: PR URL, CI status, review status.
- Must not: merge into `main` or change protected rules without approval.
- Risks: overly broad token scope, rate limits, auth failure.
- MVP: GitHub CLI `gh` with scoped token.
- Later: GitHub App installation tokens, richer PR automation.

### Repository Manager

- Responsibility: clone/fetch base repository and verify clean state.
- Inputs: repository config, default branch.
- Outputs: local repo cache path, current `origin/main`.
- Must not: write directly into the task worktree.
- Risks: stale refs, corrupted local clone, remote conflicts.
- MVP: `git fetch`, remote URL check, separate `/repos/<repo>` directory.
- Later: multiple repositories, shallow clone policy, cache repair.

### Worktree Manager

- Responsibility: create and remove task worktrees.
- Inputs: task_id, base ref, branch name.
- Outputs: `/worktrees/task-123` path.
- Must not: reuse worktrees between tasks.
- Risks: leftover locks, uncommitted changes, path traversal.
- MVP: `git worktree add -b <branch> <path> origin/main`.
- Later: cleanup policy, disk quotas, archival snapshots.

### Claude Runner

- Responsibility: planning, architecture analysis, review.
- Inputs: task input, repository context, docs, diff.
- Outputs: `plan.md`, `architecture_plan.md`, `review.md`, blocker list.
- Must not: edit implementation files in the MVP or make merge decisions.
- Risks: wrong risk estimate, overly generic plan, hallucinated files.
- MVP: subprocess wrapper around Claude Code CLI with stdout/stderr persistence.
- Later: structured JSON output, prompt templates, multi-pass review.

### Codex Runner

- Responsibility: implement the approved plan and fix review blockers.
- Inputs: `plan.md`, task context, review blockers.
- Outputs: diff, tests, commit summary, fix log.
- Must not: modify unrelated files, bypass plan approval, or merge.
- Risks: excessive diff, opportunistic refactor, broken build.
- MVP: subprocess wrapper around Codex CLI inside the task worktree.
- Later: sandbox profiles, diff budget, model selection.

### CI Watcher

- Responsibility: get CI status for the PR or commit.
- Inputs: PR URL, commit SHA.
- Outputs: success/failure/pending, details URL.
- Must not: mark a PR ready without checks or manual verification note.
- Risks: flaky CI, missing CI, timeout.
- MVP: `gh pr checks` with timeout.
- Later: GitHub Checks API, retries, flaky detection.

### Review Runner

- Responsibility: Claude review and optional CodeRabbit status.
- Inputs: PR diff, test logs, plan.
- Outputs: `review.md`, blockers, non-blocking notes.
- Must not: auto-approve merge.
- Risks: false positives, duplicated comments, unlimited review loop.
- MVP: one Claude review pass, one fix loop for blockers.
- Later: multiple reviewers, severity taxonomy, review memory.

### Notification Service

- Responsibility: send Telegram status messages.
- Inputs: task events, PR URL, failures.
- Outputs: short Telegram messages.
- Must not: send secrets or entire large logs.
- Risks: spam, message length limits, missed notification.
- MVP: compact status messages and `/log` for recent lines.
- Later: inline approvals, digest, attachments.

### Logs Storage

- Responsibility: store run files and events.
- Inputs: task input, plan, agent logs, test logs, review.
- Outputs: audit trail and debug artifacts.
- Must not: store raw secrets, full env dumps, auth headers.
- Risks: secret leakage, uncontrolled disk growth.
- MVP: `/runs/task-123/*` and redaction before write.
- Later: rotation, compression, external log sink.

## Minimal MVP Deployment

- One Linux VPS.
- One Linux user `ai-orchestrator`.
- Python worker under systemd.
- SQLite on local disk.
- GitHub CLI `gh`.
- Git.
- Claude Code CLI.
- Codex CLI.
- File directories: `/repos`, `/worktrees`, `/runs`, `/data`.
