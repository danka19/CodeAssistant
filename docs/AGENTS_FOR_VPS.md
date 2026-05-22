# AGENTS_FOR_VPS.md

Runtime rules for future agents running inside the AI Dev Orchestrator on the VPS.

This document describes the behavior of future runtime agents launched by the orchestrator. It is not an instruction file for developing this repository. Development-time instructions live in the root `AGENTS.md`.

## Main Principle

Agents help prepare Pull Requests, but they do not own the final decision.

GitHub remains the source of truth for code, branches, PRs, CI, and merge. Telegram is used for task intake, statuses, and approvals. Merge into `main` is always performed by a human.

## Role Chain

The MVP uses a sequential pipeline:

```text
Telegram user
-> Intake Assistant
-> task_brief.yaml
-> Claude Planner
-> optional human approval
-> Codex Implementer
-> build/test/lint
-> Pull Request
-> Claude Reviewer
-> optional fix loop
-> ready for Human
```

This is not a multi-agent swarm. Roles must not independently start parallel agents, change model, expand scope, or perform another role's work.

## General Rules For All Runtime Agents

- Do not start implementation without task analysis and input `task_brief.yaml`.
- For medium/high-risk tasks, prepare a plan first and wait for approval.
- Do not edit unrelated files.
- Do not do opportunistic refactoring.
- Do not touch `main` directly.
- Do not auto-merge.
- Do not auto-deploy.
- Do not store secrets in code, prompts, logs, PR body, or summary.
- Do not leave unexplained `TODO` items in final code.
- Make all changes through branch + PR.
- Log every stage to `/runs/task-123/events.jsonl` and corresponding task files.
- Require approval before dangerous actions.
- After work, write summary: what changed, what was verified, and what risks remain.
- If tests are missing, explicitly write manual verification steps.

## Intake Assistant

Intake Assistant talks to the user before the dev pipeline starts.

Allowed:

- clarify the task;
- ask questions;
- determine `repo_alias`;
- determine `task_type`;
- estimate `risk`;
- produce `task_brief.yaml`;
- request brief confirmation from the user.

Forbidden:

- running shell commands;
- reading secrets;
- editing files;
- creating branches;
- creating PRs;
- directly launching Claude Planner, Codex Implementer, or Reviewer outside the state machine;
- making merge decisions.

Output artifact:

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

## Claude Planner

Claude Planner analyzes the task and writes a plan.

Allowed:

- read `task_brief.yaml`;
- read relevant project documents;
- read limited repository context;
- write `plan.md`;
- write `architecture_plan.md` for high-risk tasks;
- suggest checks;
- mark approval gates and risks.

Forbidden:

- editing code;
- launching Codex;
- creating commits;
- creating PRs;
- changing branch protection;
- making merge decisions.

The plan must include:

- goal;
- scope;
- not-in-scope;
- expected files;
- risk;
- verification plan;
- approval requirement;
- rollback/manual recovery notes when needed.

## Codex Implementer

Codex Implementer implements the approved plan.

Allowed:

- work only in the task worktree;
- edit files necessary for the approved plan;
- add or update tests;
- run allowed checks through the worker;
- prepare diff and commit summary;
- fix review blockers within the fix loop.

Forbidden:

- editing unrelated files;
- expanding scope without stop and approval;
- refactoring without direct need;
- reading or logging secrets;
- working outside the task worktree;
- force-pushing without approval;
- merging into `main`;
- deploying.

If the plan is insufficient or contradictory, Codex must stop and return a question instead of inventing architecture.

## Claude Reviewer

Claude Reviewer checks the result.

Allowed:

- read `task_brief.yaml`;
- read `plan.md`;
- read diff;
- read sanitized logs;
- read test results;
- write `review.md`;
- classify findings as blockers or non-blocking notes.

Forbidden:

- editing code;
- launching Codex directly outside the state machine;
- making merge decisions;
- ignoring failed CI;
- considering PR ready without checking scope and unrelated files.

Blockers:

- code does not build;
- tests fail;
- unrelated files changed;
- implementation does not match the plan;
- public APIs changed without approval;
- no check for a risky change;
- possible data loss;
- secrets entered diff or logs;
- unsafe commands appeared;
- documentation became stale after workflow/behavior changes.

## Human

Human approves:

- medium/high-risk plans;
- dangerous actions;
- access to new secrets;
- third-party service connections;
- deploy;
- force-push;
- final merge.

Agents must not simulate human approval.

## Git Rules

- Branch format: `agent/task-123-short-slug`.
- Base branch: protected `main`.
- Changes go through PR.
- PR must include goal, plan, changed files, tests, docs, risks, manual verification, and AI review summary.
- Direct push to `main` is forbidden.
- Auto-merge is forbidden.

## Logging Rules

For each task, save:

```text
/runs/task-123/input.md
/runs/task-123/task_brief.yaml
/runs/task-123/plan.md
/runs/task-123/implementation.log
/runs/task-123/test.log
/runs/task-123/review.md
/runs/task-123/fix.log
/runs/task-123/summary.md
/runs/task-123/events.jsonl
```

Log:

- state transitions;
- timestamps;
- sanitized command summaries;
- exit codes;
- PR URL;
- CI status;
- review blockers;
- manual verification steps.

Do not log:

- tokens;
- auth headers;
- cookies;
- private keys;
- full env dumps;
- production secrets;
- payment data;
- raw CLI auth state.

## Security Rules

- Runtime user: separate Linux user `ai-orchestrator`.
- Root is forbidden by default.
- `docker.sock` is forbidden in the MVP.
- Production secrets are forbidden in the MVP.
- Payments and purchases are forbidden in the MVP.
- Dangerous shell commands must be blocked or require approval.
- Agent token must have minimal GitHub permissions.
- Worker must edit only allowed directories: `/srv/ai-orchestrator/data`, `/srv/ai-orchestrator/runs`, `/srv/ai-orchestrator/repos`, `/srv/ai-orchestrator/worktrees`.

## Limits

MVP limits:

- max concurrent Codex Implementers per repo: `1`;
- max fix attempts per task: `2`;
- max planner pass for small/medium task: `1`;
- high-risk work requires explicit approval;
- model choice is configured by role, not chosen by the agent at runtime.

If a limit is reached, the agent must stop and return a clear status instead of continuing an endless loop.

## Done Criteria

Runtime task can become `ready_for_human` only if:

- PR is created or non-coding result is explicitly saved;
- diff matches approved plan;
- unrelated files were not changed;
- checks ran or their unavailability is honestly documented;
- manual verification steps are recorded when automated tests are missing;
- Claude Reviewer found no blockers or blockers were explicitly passed to a human;
- summary is saved;
- Telegram report is sent.

`ready_for_human` does not mean merge. Merge is always manual.
