# AI Dev Orchestrator

A small GitHub-first AI development orchestrator for a single Linux VPS.

The MVP accepts a task from Telegram, prepares a task brief, asks Claude to produce a plan, runs Codex implementation inside a separate task worktree, executes configured checks, creates a GitHub Pull Request, runs Claude review, and reports the result back to Telegram. Merge into `main` is always manual.

## Current Phase

The repository has closed `Phase 0 - Project Bootstrap` and now implements the first slice of `Phase 1 - Telegram Intake` from [docs/12_IMPLEMENTATION_ROADMAP.md](docs/12_IMPLEMENTATION_ROADMAP.md).

What is already implemented:

- folder-first repository layout with code, config, tests, docs, and runtime placeholders split by directory;
- Python project bootstrap in `src/ai_orchestrator/`;
- tracked config template in `config/config.example.yaml`;
- minimal SQLite-backed intake flow for `/task` and `/status`;
- unit and integration tests for the current intake slice.

Still out of scope at the current phase boundary:

- task planning and approval workflow;
- Claude/Codex subprocess runners;
- GitHub branch, worktree, and PR automation;
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
