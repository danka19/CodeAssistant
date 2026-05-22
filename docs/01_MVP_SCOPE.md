# 01 MVP Scope

## MVP Goal

Build the smallest system that can run on a rented Linux VPS and support the full cycle: Telegram task -> planning -> implementation -> checks -> Pull Request -> Telegram report.

The MVP must not become a general-purpose agent platform. It must stay small, understandable, and auditable.

## MVP Must Be Able To

- Accept a task from Telegram through `/task`.
- Create a unique `task_id`.
- Store task input, status, and metadata in SQLite.
- Determine a minimal task type: small, medium, large/risky, documentation, research.
- Create a feature branch like `agent/task-123-short-slug`.
- Create a separate git worktree for the task.
- Run the Claude planning step.
- Save the plan to `/runs/task-123/plan.md`.
- Move medium/high-risk tasks to `waiting_plan_approval`.
- Run the Codex implementation step after the plan or approval.
- Store stdout/stderr and structured events.
- Run build/test/lint commands when configured for the repository.
- Record missing tests and manual verification steps.
- Create a commit in the feature branch.
- Push the feature branch.
- Create a PR through `gh pr create` or the GitHub API.
- Send a Telegram report with status, summary, checks, and PR link.
- Never merge automatically.

## Minimal MVP Entities

- `Task`: original task, status, risk, repository, branch, worktree, PR URL.
- `Run`: an attempt to execute a task.
- `Event`: a state-change log.
- `Approval`: a user decision on a plan or dangerous action.
- `CheckResult`: build/test/lint/CI/review result.

## MVP Does Not Need To Support

- Complex web UI.
- Voice input.
- Life assistant.
- Purchases and payments.
- Browser automation.
- Auto-deploy.
- Auto-merge.
- Kubernetes.
- Temporal or another workflow engine.
- Multi-agent swarm.
- Complex cost analytics.
- Multiple-user support.
- Full RBAC.
- Production secret management.

## MVP Boundaries

The MVP may be a single-process application with SQLite and file logs. The first runtime target is a `systemd` service. The main criterion is a reliable end-to-end path for one task in one repository.

Docker Compose is not part of the first MVP and remains a future option if extra isolation or reproducible runtime becomes necessary after Phase 7.

If a project has no tests or CI, the MVP must not pretend that checks passed. It must explicitly write: automated checks unavailable, manual verification required.
