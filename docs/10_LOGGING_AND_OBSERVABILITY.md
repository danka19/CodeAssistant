# 10 Logging And Observability

## Файлы на задачу

Для каждой задачи сохранять:

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

Для large/risky задач дополнительно:

```text
/runs/task-123/architecture_plan.md
/runs/task-123/approval.md
```

## Что писать в logs

- task_id, repo, branch, worktree path;
- timestamps;
- state transitions;
- команды высокого уровня;
- exit codes;
- sanitized stdout/stderr;
- ссылки на PR и CI;
- результаты checks;
- review blockers;
- manual verification steps.

## Что не писать в logs

- tokens;
- auth headers;
- cookies;
- full environment dump;
- private keys;
- production secrets;
- платежные данные;
- содержимое файлов, не относящихся к задаче;
- личные данные пользователя без необходимости.

## Redaction

Перед записью в лог worker должен применять redaction:

- значения env переменных с именами `TOKEN`, `SECRET`, `KEY`, `PASSWORD`;
- GitHub tokens;
- Telegram bot token;
- Anthropic/OpenAI auth;
- SSH private key blocks;
- URLs с credentials.

## Как смотреть статус

- Telegram: `/status task-123`.
- Telegram: `/log task-123`.
- VPS: открыть `/runs/task-123/events.jsonl`.
- GitHub: PR checks и comments.
- SQLite: task row и events.

## Как отлаживать упавшую задачу

1. Проверить `/runs/task-123/events.jsonl`.
2. Найти `failed_step`.
3. Проверить соответствующий лог: planning, implementation, test, review.
4. Проверить `git status` в worktree.
5. Проверить PR и CI, если PR уже создан.
6. Решить: manual retry, new task, close PR, request approval.

## Как повторить задачу вручную

Минимальный ручной replay:

1. Перейти в worktree задачи.
2. Проверить branch.
3. Прочитать `input.md` и `plan.md`.
4. Запустить команды проверки из `test.log` или config.
5. Запустить Codex вручную с тем же планом, если нужно.
6. Сделать commit/push вручную.
7. Обновить PR.

## Observability MVP

MVP не требует Prometheus, Grafana или distributed tracing. Достаточно SQLite state, `events.jsonl`, файловых логов и Telegram notifications.

Позже можно добавить metrics endpoint, retention policy, alerting и dashboard.

