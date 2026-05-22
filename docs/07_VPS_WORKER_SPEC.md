# 07 VPS Worker Spec

## Стек MVP

- Python.
- `python-telegram-bot` или `aiogram`.
- SQLite.
- `subprocess`.
- GitHub CLI `gh`.
- `git`.
- systemd или Docker Compose.

## Предложенная структура проекта

```text
/src/bot.py
/src/worker.py
/src/db.py
/src/config.py
/src/github_client.py
/src/repo_manager.py
/src/worktree_manager.py
/src/agent_runner.py
/src/notifier.py
/src/logger.py
/config/config.yaml
/data/tasks.sqlite
/runs/
/repos/
/worktrees/
```

## Ответственность файлов

### `/src/bot.py`

Telegram command handlers. Принимает команды, валидирует user id, пишет задачи и approvals в SQLite, отправляет короткие ответы.

### `/src/worker.py`

Основной loop state machine. Забирает queued tasks, вызывает managers/runners, меняет статусы, обрабатывает ошибки и cancellation.

### `/src/db.py`

SQLite schema, migrations, CRUD для tasks, events, approvals, runs, check results.

### `/src/config.py`

Загрузка конфигурации из env и `/config/config.yaml`. Не логирует секреты.

### `/src/github_client.py`

Обертка над `gh` или GitHub API: create PR, add labels, read checks, fetch PR URL.

### `/src/repo_manager.py`

Clone/fetch repository cache, проверка remote, base branch, clean state.

### `/src/worktree_manager.py`

Создание branch/worktree, проверка path safety, cleanup по явному запросу.

### `/src/agent_runner.py`

Запуск Claude и Codex через subprocess, timeout, capture logs, redaction.

### `/src/notifier.py`

Отправка Telegram notifications и форматирование status messages.

### `/src/logger.py`

Structured events в `events.jsonl`, файловые логи, redaction helpers.

## Команды worker

Worker должен уметь выполнять:

- `git fetch`;
- `git worktree add`;
- запуск Claude;
- запуск Codex;
- запуск тестов;
- `git status`;
- `git diff`;
- `git commit`;
- `git push`;
- `gh pr create`;
- `gh pr view`;
- `gh pr checks`.

## Конфигурация MVP

Минимальные поля:

```yaml
telegram:
  allowed_user_ids: []

github:
  default_owner: danka19

repositories:
  greenflow:
    url: git@github.com:owner/repo.git
    default_branch: main
    test_commands:
      - pytest
```

Секреты не должны храниться в `config.yaml`, если файл попадает в git. Для токенов использовать env.

## Systemd вариант

MVP может состоять из одного service:

```text
ai-orchestrator.service
```

Service запускает Python process под пользователем `ai-orchestrator`, с ограниченным working directory и env file.

## Docker Compose вариант

Docker Compose допустим, если контейнер не получает `docker.sock`, root privileges и production secrets. Для MVP systemd проще и прозрачнее.

