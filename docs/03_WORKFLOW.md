# 03 Workflow

## General Task Workflow

1. The user sends a task in Telegram.
2. The bot creates `task_id`, stores input, and sets status `queued`.
3. The worker moves the task to `planning`.
4. The repository manager updates the base repository.
5. The worktree manager creates the branch and worktree.
6. The Claude runner creates the plan.
7. If approval is required, the task waits for `/approve` or `/reject`.
8. The Codex runner implements the plan.
9. The worker runs build/test/lint when configured.
10. The worker creates a local commit after checks pass.
11. GitHub integration later pushes and creates the PR.
12. CI watcher and review runner check the result.
13. If blockers exist, a fix loop starts or the task moves to `needs_fix`.
14. The notification service sends the report and PR URL.
15. A human reviews and merges manually.

## A. Small Task

Examples: small bugfix, documentation touch-up, simple config edit, local test fix.

Behavior:

- Manual plan approval is not required.
- Claude writes a short `plan.md`.
- Codex implements immediately after planning.
- Git diff/status and available checks are required.
- Local commit is created automatically after checks pass.
- Review gate remains required, but can be short.

Flow:

```text
/task
-> queued
-> planning
-> short plan.md
-> implementing
-> testing
-> creating_pr
-> reviewing
-> ready_for_human
```

## B. Medium Task

Examples: new feature in an existing module, workflow change, multi-file edit, low-risk migration.

Behavior:

- Claude writes a full `plan.md`.
- The user approves the plan through `/approve task-123`.
- Codex implements only the approved plan.
- Claude review is required.
- If blockers exist, a Codex fix loop starts.
- PR is created after checks and summary.

Flow:

```text
/task
-> queued
-> planning
-> waiting_plan_approval
-> approved
-> implementing
-> testing
-> reviewing
-> needs_fix or creating_pr
-> ready_for_human
```

## C. Large/Risky Task

Examples: architectural change, large refactor, public API change, C++/Qt concurrency, external SDK integration, potential data loss.

Behavior:

- Claude writes `architecture_plan.md`.
- The user approves the architecture plan.
- The task may be split into multiple GitHub issues.
- Implementation proceeds in stages.
- Each stage may have a separate branch or PR.
- Review gate is strict: CI, Claude review, optional independent critic, human review.
- Fix loop is limited to avoid endless edits.

Flow:

```text
/task
-> planning
-> architecture_plan.md
-> waiting_plan_approval
-> split into issues if needed
-> staged implementation
-> PR per stage
-> strict review
-> manual merge only
```

## Non-Coding Task Mode

Non-coding tasks do not need to create an implementation diff.

Types:

- research;
- documentation;
- project planning;
- architecture analysis;
- monitoring;
- future life-assistant tasks.

Rules:

- Research must save `summary.md` and sources when external context was used.
- Documentation tasks may create PRs with docs-only changes.
- Project planning must explicitly separate accepted decisions from open questions.
- Monitoring after MVP should be a separate scheduled mode, not mixed into the dev-agent loop.
- Future life-assistant tasks must live in a separate security domain and must not receive access to dev secrets.

## Documentation Update Step

Any task that changes behavior, policy, architecture, workflow, state transitions, or operator process must include a documentation update step before final completion.

Minimum expectation:

- update the canonical source document for the changed topic;
- record the task result in the task log layer;
- update current-state material when factual project status changed;
- create or update a decision record when a durable choice was made.

The operational rules for this are defined in `docs/20_DOCUMENTATION_OPERATIONS.md`.
