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

Telegram command handlers, polling runtime adapter, and response formatting. The current implementation includes `/task`, `/tasks`, `/status`, `/approve`, `/reject`, `/help`, and a polling startup path.

### `/src/ai_orchestrator/worker/`

Worker boundary. The current implementation includes manual operator bridges for repository/worktree preparation and Claude planning; implementer and review execution still remain for later phases.

### `/src/ai_orchestrator/db/`

SQLite schema and repository code. Phase 1 currently stores tasks and events only.

### `/src/ai_orchestrator/config/`

Loads typed configuration from `config/config.example.yaml` or a deployment config file. Does not log secrets.

### `/src/ai_orchestrator/services/`

Application service layer. The current implementation holds intake logic, authorization checks, and the manual planning artifact workflow.

### `/src/ai_orchestrator/notifier/`

Notification boundary. Phase 1 uses simple Telegram text formatting only.

### `/src/ai_orchestrator/integrations/github_client.py`

Wrapper around `gh` or GitHub API: current Phase 2 implementation validates auth through `gh auth status`; later phases add PR creation, labels, checks, and PR URL fetches.

### `/src/ai_orchestrator/integrations/claude_runner.py`

Claude planning/review runner boundary. The current Phase 3 slice runs the configured planner command in non-interactive print mode and captures stdout/stderr for persisted planning artifacts.

### `/src/ai_orchestrator/integrations/codex_runner.py`

Codex implementation runner boundary. The current Phase 4 slice runs non-interactive `codex exec` in the task worktree, captures stdout/stderr, and surfaces execution failures to the implementation service.

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

Current implementation note:

- Phase 1 does not run worker commands.
- The current Phase 2 slice can run repository preparation commands through the manual `prepare-workspace` CLI bridge only.
- The current Phase 2 slice can also validate GitHub CLI auth through the manual `check-github-auth` CLI bridge.
- The current Phase 3 slice can run Claude planning through the manual `plan-task` CLI bridge.
- The current Phase 4 slice can run Codex implementation through the manual `implement-task` CLI bridge, persist implementation and test logs, capture git status/diff summary, run configured checks, create a local commit only after checks pass, and hand the task off into `creating_pr`.

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

Phase 1 startup command can be:

```text
ai-orchestrator --config /srv/ai-orchestrator/config/config.yaml --database-path /srv/ai-orchestrator/data/tasks.sqlite3
```

Current Phase 2 operator bridge:

```text
ai-orchestrator prepare-workspace --config /srv/ai-orchestrator/config/config.yaml --database-path /srv/ai-orchestrator/data/tasks.sqlite3 --task-id task-123 --repo-alias codeassistant
```

Current Phase 2 GitHub auth check:

```text
ai-orchestrator check-github-auth --config /srv/ai-orchestrator/config/config.yaml --database-path /srv/ai-orchestrator/data/tasks.sqlite3
```

Current Phase 3 planner bridge:

```text
ai-orchestrator plan-task --config /srv/ai-orchestrator/config/config.yaml --database-path /srv/ai-orchestrator/data/tasks.sqlite3 --task-id task-123 --risk medium
```

Current Phase 4 implementer bridge:

```text
ai-orchestrator implement-task --config /srv/ai-orchestrator/config/config.yaml --database-path /srv/ai-orchestrator/data/tasks.sqlite3 --task-id task-123
```

## Docker Compose

Docker Compose is not part of the first MVP. For Phase 0-1, `systemd` is selected because it is simpler for the first VPS launch, interactive Claude/Codex CLI authorization, `git`, `gh`, SSH, worktrees, and file logs.

Docker Compose can be reconsidered after Phase 7 if reproducible runtime or extra isolation becomes necessary. Do not expose `docker.sock` to agents in the MVP.
