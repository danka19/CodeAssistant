# 16 MVP Decisions

Decision date: 2026-05-22.

This document records selected decisions for the first MVP. If earlier documents describe multiple options, the decisions below are authoritative for Phase 0-1.

## 1. Runtime Mode

Selected option A: `systemd`.

Reasons:

- fewer layers for the first VPS launch;
- easier work with `git`, `gh`, SSH, worktrees, and file logs;
- easier Claude/Codex CLI authorization under a dedicated Linux user;
- easier debugging through `journalctl` and `/runs`.

Docker Compose is not part of the first MVP. It can be reconsidered in Phase 7 if reproducible runtime or extra isolation becomes necessary. Do not expose `docker.sock` to agents in the MVP.

## 2. Repo Aliases

The MVP uses two aliases.

```yaml
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

`codeassistant` is used for developing the orchestrator itself. `sandbox-py` is a safe test repository for early end-to-end runs.

## 3. CI/Test Commands

For the first Python repository, use the recommended set:

```bash
python -m compileall src tests
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

Minimal test areas for the orchestrator itself:

- SQLite schema and migrations;
- task state transitions;
- branch slug generation;
- command allowlist/blocklist;
- secret redaction;
- fake Claude/Codex runners;
- fake GitHub client;
- temporary git repo integration test for worktree.

If the `tests` directory does not exist yet, the `compileall` command must be adapted during Phase 0 implementation. The documentation goal remains unchanged: automated checks must be explicit, and their absence must not be hidden.

## 4. GitHub Auth

Selected option A: fine-grained Personal Access Token.

Minimum permissions:

- selected repositories only;
- `Contents: read/write`;
- `Pull requests: read/write`;
- `Issues: read/write`, optional for future task splitting;
- `Metadata: read`.

Do not grant for MVP:

- `Administration`;
- `Secrets`;
- `Environments`;
- `Deployments`;
- `Workflows`, unless there is a separate need.

GitHub App remains a future option. `github_client.py` should be designed so PAT auth can later be replaced with GitHub App auth without rewriting the whole workflow.

## 5. Claude/Codex CLI Auth

Selected option A: interactive CLI authorization under Linux user `ai-orchestrator`.

Rules:

- Claude CLI and Codex CLI are authorized manually over SSH once under the same user that runs the worker;
- worker must not log auth state, token files, env, or CLI config;
- API-key mode should not be enabled until needed for reliability, limits, or transparent cost;
- cost and limits must be tracked as an open operational question;
- if login-based mode becomes unstable or cost-opaque, return to an API-key variant with explicit budget control.

## 6. MVP Role Chain

Selected sequential pipeline of four roles:

```text
Telegram user
-> Intake Assistant
-> approved Task Brief
-> Claude Planner
-> Codex Implementer
-> Claude Reviewer
-> PR ready for Human
```

This is not a multi-agent swarm. In the MVP, roles run sequentially with strict responsibility boundaries and typed handoff between stages.

## 7. Intake Assistant

Intake Assistant sits before the dev orchestrator and helps formulate the task before development starts.

Responsibilities:

- discuss the task with the user;
- clarify goal, constraints, and expected result;
- determine repo alias;
- suggest task type and risk level;
- produce `task_brief.yaml`;
- request brief confirmation before passing to the dev pipeline unless the task is clearly small;
- not run git, shell, Claude Planner, Codex, or PR creation directly.

Forbidden:

- editing files;
- having write access to git;
- accessing production secrets;
- running shell commands;
- creating PRs;
- making merge decisions.

Minimal intake states:

```text
drafting
waiting_brief_approval
submitted_to_orchestrator
cancelled
```

## 8. Typed Handoff

Intake Assistant passes only a typed brief.

```yaml
task_brief:
  task_id: task-123
  repo_alias: codeassistant
  title: "Short human-readable title"
  task_type: bugfix | feature | docs | research | refactor
  risk: low | medium | high
  problem: "What is wrong or missing"
  desired_outcome: "What should be true after the task"
  acceptance_criteria:
    - "Observable criterion"
  constraints:
    - "What must be preserved"
  not_in_scope:
    - "What must not be changed"
  approval_required: true
  suggested_checks:
    - "python -m pytest -q"
```

`task_brief.yaml` is saved in `/runs/task-123/input.md` or `/runs/task-123/task_brief.yaml` and becomes the main input for Claude Planner.

## 9. Claude Planner

Claude Planner receives `task_brief.yaml`, project documents, and limited repository context.

Responsibilities:

- create `plan.md` for small/medium tasks;
- create `architecture_plan.md` for high-risk tasks;
- explicitly state scope and not-in-scope;
- propose verification commands;
- mark whether approval is required;
- not edit files or run implementation.

## 10. Codex Implementer

Codex Implementer receives the approved `plan.md` and works only inside the task worktree.

Responsibilities:

- implement the plan;
- add or update tests;
- avoid unrelated files;
- stop and require new approval before expanding scope;
- prepare diff, commit summary, and verification notes.

MVP constraint: no more than one Codex Implementer per repository at the same time.

## 11. Claude Reviewer

Claude Reviewer receives the task brief, plan, diff, logs, and test results.

Responsibilities:

- verify that implementation matches the plan;
- find blockers;
- separate blockers from non-blocking notes;
- write `review.md`;
- not edit code directly.

The fix loop is limited to one or two attempts. If blockers remain, the task moves to `needs_fix` or `failed` with a clear reason.

## 12. Models, Limits, And Parallelism

The MVP must fix role, model, and limits in config instead of letting agents choose them independently.

Minimal policy:

- `intake_assistant`: cheap/fast model or local logic, no write tools;
- `claude_planner`: Claude, planning/review context;
- `codex_implementer`: Codex CLI, write access only in worktree;
- `claude_reviewer`: Claude, read-only review context;
- max concurrent implementers per repo: `1`;
- max fix attempts: `2`;
- max planner pass: `1` for small/medium, separate approval for high risk.

The goal of these limits is to avoid burning limits and creating conflicting parallel diffs.

## 13. Knowledge System Decision

The project adopts an Obsidian-style knowledge method without coupling the product to the Obsidian application itself.

Decision:

- knowledge is stored in normal repository Markdown files;
- the method uses atomic notes, map documents, decision records, strong linking, and explicit status metadata;
- current state, plans, decisions, logs, and policy must remain separate;
- documentation maintenance is part of task completion, not optional cleanup.

Why:

- future agents need reliable retrieval of current truth;
- future services must not inherit unsafe or irrelevant rules by accident;
- the platform needs a scalable model for multi-agent and multi-service growth without a heavy documentation platform in MVP.

Follow-up docs:

- `docs/19_AGENT_KNOWLEDGE_SYSTEM.md`
- `docs/20_DOCUMENTATION_OPERATIONS.md`
- `docs/21_PILOT_KNOWLEDGE_SYSTEM_PLAN.md`
