# Runtime Role Contracts

Status: active
Audience: future runtime agents and maintainers
Owner: repository maintainers
Update when: runtime role responsibilities or handoff contracts change

## Common Rules For All Runtime Agents

- Do not start implementation without the input task brief.
- For medium or high-risk tasks, produce a plan and wait for approval when required.
- Do not change unrelated files.
- Do not perform opportunistic refactoring.
- Do not touch `main` directly.
- Do not auto-merge.
- Do not auto-deploy.
- Do not store secrets in code, prompts, logs, PR bodies, or summaries.
- Require approval before dangerous actions.
- Log each stage into the task run directory.
- Produce a summary stating what changed, what was verified, and which risks remain.

## Intake Assistant

Allowed:

- clarify the task with the user;
- determine `repo_alias`, `task_type`, and `risk`;
- prepare `task_brief.yaml`;
- request confirmation of the brief.

Forbidden:

- running shell commands;
- reading secrets;
- editing repository files;
- creating branches or PRs;
- calling Planner, Implementer, or Reviewer outside the state machine;
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

Allowed:

- read `task_brief.yaml`;
- read relevant project documents and limited repository context;
- write `plan.md`;
- write `architecture_plan.md` for high-risk tasks;
- propose checks, approval gates, and risks.

Forbidden:

- editing code;
- launching implementation directly;
- creating commits or PRs;
- making merge decisions.

## Codex Implementer

Allowed:

- work only inside the task worktree;
- change files required by the approved plan;
- add or update tests;
- run approved checks through the worker;
- prepare diff and commit summary;
- address review blockers inside the fix loop.

Forbidden:

- changing unrelated files;
- expanding scope without a new decision;
- reading or logging secrets;
- working outside the task worktree;
- force-pushing without approval;
- merging or deploying.

## Claude Reviewer

Allowed:

- read `task_brief.yaml`, `plan.md`, diffs, sanitized logs, and test results;
- write `review.md`;
- classify findings as blockers or non-blocking notes.

Forbidden:

- editing code;
- bypassing the state machine;
- making merge decisions;
- ignoring failed CI or scope drift.

Typical blockers:

- build or tests fail;
- unrelated files changed;
- implementation does not match the plan;
- risky public API change happened without approval;
- required verification is missing;
- data-loss risk appears;
- secrets appear in diffs or logs.

## Human

The human approves:

- medium or high-risk plans;
- dangerous actions;
- new secret access;
- new third-party service integration;
- deploys;
- force-pushes;
- final merge.
