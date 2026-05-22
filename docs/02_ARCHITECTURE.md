# 02 Architecture

## Общая схема

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

## Компоненты

### Telegram Bot

- Ответственность: принимает команды пользователя и отправляет уведомления.
- Входы: `/task`, `/status`, `/log`, `/approve`, `/reject`, `/cancel`, `/help`.
- Выходы: записи в SQLite, events, Telegram messages.
- Не должен делать: запускать shell-команды, хранить секреты в сообщениях, принимать merge decisions.
- Риски: spoofing пользователя, потеря контекста, слишком длинные сообщения.
- MVP: один разрешенный Telegram user id, polling или webhook, минимальные команды.
- Позже: multiple users, roles, inline buttons, richer status cards.

### API/Worker Process

- Ответственность: основной glue-layer и state machine.
- Входы: задачи из SQLite, approvals, cancel events.
- Выходы: запуски git, Claude, Codex, tests, GitHub PR, notifications.
- Не должен делать: обходить security gates, выполнять неразрешенные destructive команды.
- Риски: зависшие subprocess, partial failure, race conditions.
- MVP: один worker loop, блокировка задачи на время выполнения.
- Позже: очередь, retries, parallel workers, supervisor.

### SQLite Database

- Ответственность: хранение task state, approvals, events, paths, PR metadata.
- Входы: команды bot и worker events.
- Выходы: состояние для `/status`, worker loop и audit.
- Не должен делать: хранить секреты и полные agent prompts с credentials.
- Риски: corruption при неправильных concurrent writes, отсутствие backups.
- MVP: локальный файл `/data/tasks.sqlite`, WAL mode, простые migrations.
- Позже: PostgreSQL, retention policy, task search.

### GitHub Integration

- Ответственность: push branch, create PR, read CI status, labels, comments.
- Входы: branch, commit, PR body, labels.
- Выходы: PR URL, CI status, review status.
- Не должен делать: merge в `main`, менять protected rules без approval.
- Риски: token scope слишком широкий, rate limits, auth failure.
- MVP: GitHub CLI `gh` с scoped token или GitHub App.
- Позже: GitHub App installation tokens, richer PR automation.

### Repository Manager

- Ответственность: clone/fetch базового репозитория, проверка clean state.
- Входы: repository config, default branch.
- Выходы: локальный путь repo cache, актуальный `origin/main`.
- Не должен делать: писать в worktree задачи напрямую.
- Риски: stale refs, поврежденный local clone, конфликт remote.
- MVP: `git fetch`, проверка remote URL, отдельная папка `/repos/<repo>`.
- Позже: multiple repositories, shallow clone policy, cache repair.

### Worktree Manager

- Ответственность: создавать и удалять task worktree.
- Входы: task_id, base ref, branch name.
- Выходы: path `/worktrees/task-123`.
- Не должен делать: reuse worktree между задачами.
- Риски: leftover locks, uncommitted changes, path traversal.
- MVP: `git worktree add -b <branch> <path> origin/main`.
- Позже: cleanup policy, disk quotas, archival snapshots.

### Claude Runner

- Ответственность: planning, architecture analysis, review.
- Входы: task input, repository context, docs, diff.
- Выходы: `plan.md`, `architecture_plan.md`, `review.md`, blocker list.
- Не должен делать: менять файлы реализации в MVP, принимать merge decisions.
- Риски: неверная оценка риска, слишком общий план, hallucinated files.
- MVP: subprocess wrapper вокруг Claude Code CLI, сохранение stdout/stderr.
- Позже: structured JSON output, prompt templates, multi-pass review.

### Codex Runner

- Ответственность: реализация утвержденного плана и fix loop.
- Входы: `plan.md`, task context, review blockers.
- Выходы: diff, tests, commit summary, fix log.
- Не должен делать: менять unrelated files, обходить plan approval, merge.
- Риски: чрезмерный diff, opportunistic refactor, broken build.
- MVP: subprocess wrapper вокруг Codex CLI в task worktree.
- Позже: sandbox profiles, diff budget, model selection.

### CI Watcher

- Ответственность: получить статус CI для PR или commit.
- Входы: PR URL, commit SHA.
- Выходы: success/failure/pending, details URL.
- Не должен делать: считать PR готовым без проверок или manual verification note.
- Риски: flaky CI, missing CI, timeout.
- MVP: `gh pr checks` с timeout.
- Позже: GitHub Checks API, retries, flaky detection.

### Review Runner

- Ответственность: Claude review и optional CodeRabbit status.
- Входы: PR diff, test logs, plan.
- Выходы: `review.md`, blockers, non-blocking notes.
- Не должен делать: auto-approve merge.
- Риски: false positives, duplicated comments, review loop без лимита.
- MVP: один Claude review pass, один fix loop при blockers.
- Позже: multiple reviewers, severity taxonomy, review memory.

### Notification Service

- Ответственность: отправка Telegram-сообщений о статусах.
- Входы: task events, PR URL, failures.
- Выходы: короткие Telegram messages.
- Не должен делать: отправлять секреты, большие логи целиком.
- Риски: spam, message length limits, missed notification.
- MVP: compact status messages и `/log` для последних строк.
- Позже: inline approvals, digest, attachments.

### Logs Storage

- Ответственность: хранение файлов запуска и events.
- Входы: task input, plan, agent logs, test logs, review.
- Выходы: audit trail и debug artifacts.
- Не должен делать: хранить raw secrets, full env dumps, auth headers.
- Риски: утечка секретов, неконтролируемый рост диска.
- MVP: `/runs/task-123/*` и redaction before write.
- Позже: rotation, compression, external log sink.

## Минимальная MVP-развертка

- Один Linux VPS.
- Один Linux user `ai-orchestrator`.
- Python worker под systemd или Docker Compose.
- SQLite на локальном диске.
- GitHub CLI `gh`.
- Git.
- Claude Code CLI.
- Codex CLI.
- Файловые директории: `/repos`, `/worktrees`, `/runs`, `/data`.

