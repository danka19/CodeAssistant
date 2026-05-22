# 07 VPS Worker Spec

## MVP Stack

- Python.
- `python-telegram-bot` or `aiogram`.
- SQLite.
- `subprocess`.
- GitHub CLI `gh`.
- `git`.
- systemd.

## Proposed Project Structure

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

## File Responsibilities

### `/src/bot.py`

Telegram command handlers. Accepts commands, validates user id, writes tasks and approvals to SQLite, sends short responses.

### `/src/worker.py`

Main state-machine loop. Takes queued tasks, calls managers/runners, changes statuses, handles errors and cancellation.

### `/src/db.py`

SQLite schema, migrations, CRUD for tasks, events, approvals, runs, and check results.

### `/src/config.py`

Loads configuration from env and `/config/config.yaml`. Does not log secrets.

### `/src/github_client.py`

Wrapper around `gh` or GitHub API: create PR, add labels, read checks, fetch PR URL.

### `/src/repo_manager.py`

Clone/fetch repository cache, validate remote, base branch, and clean state.

### `/src/worktree_manager.py`

Branch/worktree creation, path safety checks, cleanup on explicit request.

### `/src/agent_runner.py`

Runs Claude and Codex through subprocess, timeout, log capture, and redaction.

### `/src/notifier.py`

Sends Telegram notifications and formats status messages.

### `/src/logger.py`

Structured events in `events.jsonl`, file logs, redaction helpers.

## Worker Commands

The worker must be able to run:

- `git fetch`;
- `git worktree add`;
- Claude;
- Codex;
- tests;
- `git status`;
- `git diff`;
- `git commit`;
- `git push`;
- `gh pr create`;
- `gh pr view`;
- `gh pr checks`.

## MVP Configuration

Minimal fields:

```yaml
telegram:
  allowed_user_ids: []

github:
  default_owner: danka19

repositories:
  codeassistant:
    repo: danka19/CodeAssistant
    default_branch: main
    purpose: orchestrator_self_development
    local_path: /srv/ai-orchestrator/repos/codeassistant
    worktree_root: /srv/ai-orchestrator/worktrees/codeassistant
    test_commands:
      - python -m compileall src tests
      - python -m pytest -q
      - python -m ruff check .
      - python -m ruff format --check .

  sandbox-py:
    repo: danka19/ai-orchestrator-sandbox
    default_branch: main
    purpose: safe_end_to_end_test_repository
    local_path: /srv/ai-orchestrator/repos/sandbox-py
    worktree_root: /srv/ai-orchestrator/worktrees/sandbox-py
    test_commands:
      - python -m compileall src tests
      - python -m pytest -q
      - python -m ruff check .
      - python -m ruff format --check .
```

Secrets must not be stored in `config.yaml` if the file is committed. Use env for tokens.

## Systemd Variant

The MVP may consist of one service:

```text
ai-orchestrator.service
```

The service runs the Python process under user `ai-orchestrator`, with a restricted working directory and env file.

## Docker Compose

Docker Compose is not part of the first MVP. For Phase 0-1, `systemd` is selected because it is simpler for the first VPS launch, interactive Claude/Codex CLI authorization, `git`, `gh`, SSH, worktrees, and file logs.

Docker Compose can be reconsidered after Phase 7 if reproducible runtime or extra isolation becomes necessary. Do not expose `docker.sock` to agents in the MVP.
