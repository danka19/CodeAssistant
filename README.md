# AI Dev Orchestrator

A small GitHub-first AI development orchestrator for a single Linux VPS.

The MVP accepts a task from Telegram, prepares a task brief, asks Claude to produce a plan, runs Codex implementation inside a separate task worktree, executes configured checks, creates a GitHub Pull Request, runs Claude review, and reports the result back to Telegram. Merge into `main` is always manual.

## Current Phase

The repository has completed the initial minimal implementation for `Phase 1 - Telegram Intake` from [docs/12_IMPLEMENTATION_ROADMAP.md](docs/12_IMPLEMENTATION_ROADMAP.md). Work is now in `Phase 2 - GitHub/Repo Manager`, with repository/worktree preparation foundations and a manual worker bridge landed for operator-driven workspace setup.

What is already implemented:

- folder-first repository layout with code, config, tests, docs, and runtime placeholders split by directory;
- Python project bootstrap in `src/ai_orchestrator/`;
- tracked config template in `config/config.example.yaml`;
- runnable Telegram polling intake bot for `/task`, `/tasks`, `/status`, and `/help`;
- task browsing through `/tasks` with Telegram buttons that open per-task status;
- SQLite-backed task/event persistence plus allowlist checks;
- CLI entrypoint: `python -m ai_orchestrator.app` or `ai-orchestrator`;
- manual Phase 2 worker bridge: `prepare-workspace --task-id <task-id> --repo-alias <alias>`;
- unit and integration tests for the completed Phase 1 intake flow.

Still out of scope at the current phase boundary:

- task planning and approval workflow;
- Claude/Codex subprocess runners;
- full automatic GitHub branch/worktree/PR automation from intake through planner;
- full worker execution loop;
- `/log`, `/approve`, `/reject`, and `/cancel`;
- Docker Compose, Kubernetes, dashboards, or auto-deploy.

## Repository Layout

The repository keeps future development out of the root whenever possible.

- `src/` contains Python application code.
- `tests/` contains unit and integration tests.
- `config/` contains tracked templates and configuration notes.
- `docs/` contains policy, architecture, plans, state, logs, and workflow documentation.
- `data/`, `runs/`, `repos/`, and `worktrees/` exist as runtime placeholders only; their contents are not tracked.

The root is reserved for entrypoints and tooling such as `AGENTS.md`, `README.md`, `pyproject.toml`, and `.gitignore`.

## Fixed MVP Decisions

The active decision record is [docs/16_MVP_DECISIONS.md](docs/16_MVP_DECISIONS.md).

Current fixed choices:

- runtime: `systemd`;
- language: Python;
- storage: SQLite plus file logs;
- GitHub auth: fine-grained Personal Access Token;
- Claude/Codex auth: interactive CLI login under Linux user `ai-orchestrator`;
- repo aliases: `codeassistant` and `sandbox-py`;
- checks: `compileall`, `pytest`, `ruff check`, `ruff format --check`;
- no auto-merge;
- no auto-deploy;
- no Docker Compose in the first MVP.

## Phase 1 Local Run

Minimal local smoke-test:

1. Install dependencies.
2. Put the real bot token into environment variable `TELEGRAM_BOT_TOKEN`.
3. Put your Telegram numeric user id either into `telegram.allowed_user_ids` in config or into env variable `TELEGRAM_ALLOWED_USER_IDS`.
4. Run `python -m ai_orchestrator.app --config config/config.example.yaml --database-path data/tasks.sqlite3`.
5. In Telegram, test `/help`, `/task test intake`, `/tasks`, and `/status <task_id>`.

Repository-side verification for this branch also includes a real local entrypoint launch check through `python run_bot.py --help` plus a startup attempt with test env values. In this environment the startup path reaches Telegram client initialization and then stops on outbound network failure, which is the current limit of local live verification here.

The app also auto-loads `.env.local` from the repository root, so for local manual testing you can put the token there instead of exporting it in the shell.

You can also use the installed script entrypoint:

```bash
ai-orchestrator --config config/config.example.yaml --database-path data/tasks.sqlite3
```

If you prefer keeping Telegram token and allowlist next to each other, create `.env.local` in the repo root:

```text
TELEGRAM_BOT_TOKEN=123456:real-token
TELEGRAM_ALLOWED_USER_IDS=123456789
```

Or run directly from the repository root without package installation:

```bash
python run_bot.py --config config/config.example.yaml --database-path data/tasks.sqlite3
```

## Phase 2 Operator Bridge

The current Phase 2 slice adds a manual operator-facing bridge for repository preparation before the planner exists in runtime:

```bash
python -m ai_orchestrator.app prepare-workspace --task-id task-123 --repo-alias codeassistant
```

This command:

- loads the configured repository alias;
- clones or refreshes the cached repository under the managed `repos/` root;
- creates branch `agent/task-...`;
- creates a dedicated task worktree under the managed `worktrees/` root;
- records git command events and updates the task status to `planning`.

## Documentation Map

- [docs/00_PROJECT_OVERVIEW.md](docs/00_PROJECT_OVERVIEW.md) - project overview and boundaries.
- [docs/01_MVP_SCOPE.md](docs/01_MVP_SCOPE.md) - MVP scope.
- [docs/02_ARCHITECTURE.md](docs/02_ARCHITECTURE.md) - components and responsibilities.
- [docs/03_WORKFLOW.md](docs/03_WORKFLOW.md) - task workflows by risk level.
- [docs/04_SECURITY_MODEL.md](docs/04_SECURITY_MODEL.md) - security model and approval gates.
- [docs/05_AGENT_ROLES.md](docs/05_AGENT_ROLES.md) - runtime role boundaries.
- [docs/07_VPS_WORKER_SPEC.md](docs/07_VPS_WORKER_SPEC.md) - VPS worker specification.
- [docs/08_GITHUB_FLOW.md](docs/08_GITHUB_FLOW.md) - branch and PR flow.
- [docs/09_TASK_STATES.md](docs/09_TASK_STATES.md) - task state machine.
- [docs/10_LOGGING_AND_OBSERVABILITY.md](docs/10_LOGGING_AND_OBSERVABILITY.md) - logs and observability.
- [docs/11_CI_AND_REVIEW_GATES.md](docs/11_CI_AND_REVIEW_GATES.md) - CI and review gates.
- [docs/12_IMPLEMENTATION_ROADMAP.md](docs/12_IMPLEMENTATION_ROADMAP.md) - implementation phases.
- [docs/13_MVP_ACCEPTANCE_CRITERIA.md](docs/13_MVP_ACCEPTANCE_CRITERIA.md) - acceptance criteria.
- [docs/16_MVP_DECISIONS.md](docs/16_MVP_DECISIONS.md) - canonical MVP decisions.

## Example Configuration

Start from [config/config.example.yaml](config/config.example.yaml).

The file contains placeholders only and is safe to commit. Do not put real tokens, CLI auth state, SSH private keys, cookies, or production secrets in tracked config files. Runtime secrets must live in a systemd environment file or another deployment secret mechanism outside git.

## Expected Runtime Layout

The VPS runtime stores mutable state under `/srv/ai-orchestrator`:

```text
/srv/ai-orchestrator/data
/srv/ai-orchestrator/runs
/srv/ai-orchestrator/repos
/srv/ai-orchestrator/worktrees
```

Generated runtime data, local SQLite databases, worktrees, cloned repositories, logs, CLI auth state, and `.env` files must not be committed.

## Verification

Use the configured project checks:

```bash
python -m compileall src tests
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```
