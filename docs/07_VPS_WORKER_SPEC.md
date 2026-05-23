# 07 VPS Worker Spec

## MVP Stack

- Python.
- `python-telegram-bot`.
- SQLite.
- `subprocess`.
- GitHub CLI `gh`.
- `git`.
- systemd.

## Proposed Project Structure

```text
/src/ai_orchestrator/app.py
/src/ai_orchestrator/bot/
/src/ai_orchestrator/worker/
/src/ai_orchestrator/db/
/src/ai_orchestrator/config/
/src/ai_orchestrator/services/
/src/ai_orchestrator/notifier/
/src/ai_orchestrator/integrations/
/src/ai_orchestrator/shared/
/tests/unit/
/tests/integration/
/config/config.example.yaml
/data/tasks.sqlite
/runs/
/repos/
/worktrees/
```

## File Responsibilities

### `/src/ai_orchestrator/bot/`

Telegram command handlers and response formatting. Phase 1 currently implements `/task` and `/status`.

### `/src/ai_orchestrator/worker/`

Worker boundary. Phase 1 keeps this as a stub so the repository structure is ready before later workflow phases.

### `/src/ai_orchestrator/db/`

SQLite schema and repository code. Phase 1 currently stores tasks and events only.

### `/src/ai_orchestrator/config/`

Loads typed configuration from `config/config.example.yaml` or a deployment config file. Does not log secrets.

### `/src/ai_orchestrator/services/`

Application service layer. Phase 1 currently holds intake logic and authorization checks.

### `/src/ai_orchestrator/notifier/`

Notification boundary. Phase 1 uses simple Telegram text formatting only.

### `/src/ai_orchestrator/integrations/github_client.py`

Wrapper around `gh` or GitHub API: create PR, add labels, read checks, fetch PR URL.

### `/src/ai_orchestrator/integrations/claude_runner.py`

Claude planning/review runner placeholder for later phases.

### `/src/ai_orchestrator/integrations/codex_runner.py`

Codex implementation runner placeholder for later phases.

### `/src/ai_orchestrator/shared/`

Shared enums, id generation, clock helpers, and small shared types.

## Worker Commands

The full worker will eventually need to run:

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

Phase 1 does not run these commands yet.

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

Secrets must not be stored in tracked config templates. Use env for tokens.

Tracked template path for the repository: `config/config.example.yaml`.

## Systemd Variant

The MVP may consist of one service:

```text
ai-orchestrator.service
```

The service runs the Python process under user `ai-orchestrator`, with a restricted working directory and env file.

## Docker Compose

Docker Compose is not part of the first MVP. For Phase 0-1, `systemd` is selected because it is simpler for the first VPS launch, interactive Claude/Codex CLI authorization, `git`, `gh`, SSH, worktrees, and file logs.

Docker Compose can be reconsidered after Phase 7 if reproducible runtime or extra isolation becomes necessary. Do not expose `docker.sock` to agents in the MVP.
