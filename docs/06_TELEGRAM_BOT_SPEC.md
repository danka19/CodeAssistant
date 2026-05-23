# 06 Telegram Bot Spec

## Purpose

The Telegram bot is the main user interface for the MVP.

For the MVP, one allowed Telegram user id is sufficient.

Current implementation status:

- implemented in the initial minimal Phase 1 intake foundation: Telegram polling runtime, `/task`, `/tasks`, `/status`, `/help`, allowlist validation, SQLite persistence for tasks and events;
- hotfix added after Phase 2 verification: limited retries for transient Telegram reply timeouts in the polling runtime;
- Phase 3 now adds `/approve` and `/reject` for tasks waiting on manual plan approval;
- planned for later phases: `/log`, `/cancel`, and richer notifications tied to planner/implementer/review stages.

Planned near-term bot improvements:

- keep improving operator-facing Telegram setup ergonomics around deployment-side env/config files;
- extend task interaction further only if the `/tasks` menu needs pagination, filtering, or richer per-task actions.

## Commands

### `/task`

- Purpose: create a new task.
- Format: `/task <task description>`.
- Example: `/task Fix crash when camera window closes`.
- Behavior: creates `task_id`, stores input text, and sets status `queued`.
- Status: current implementation returns `queued`.
- Errors: empty description, unauthorized user, database unavailable.
- Response: `Task task-123 accepted. Status: queued.`

### `/status`

- Purpose: show task state.
- Format: `/status <task_id>`.
- Example: `/status task-123`.
- Behavior: reads SQLite and returns the current stored task status.
- Status: unchanged.
- Errors: task not found, user not allowed.
- Response: `task-123: queued.`

### `/tasks`

- Purpose: browse existing tasks through a Telegram menu.
- Format: `/tasks`.
- Behavior: returns a compact Telegram button list where each button is labeled with the task title.
- Current interaction: clicking a task button opens the selected task status view using that task id.
- Status: implemented.
- Errors: user not allowed, no tasks available, database unavailable.
- Response: button menu plus fallback text when no tasks exist.

### `/log`

- Purpose: show recent task log lines.
- Format: `/log <task_id>`.
- Example: `/log task-123`.
- Behavior: returns a tail from `events.jsonl` and key logs.
- Status: unchanged.
- Errors: task not found, logs unavailable, log too large.
- Response: short secret-free fragment.

Current phase note: not implemented in Phase 1.

### `/approve`

- Purpose: approve a plan or gated action.
- Format: `/approve <task_id>`.
- Example: `/approve task-123`.
- Behavior: records an approval event.
- Status: `waiting_plan_approval` -> `implementing`.
- Errors: task not found, task not waiting for approval, user not allowed.
- Response: `task-123 approved. Status: implementing.`

Current phase note: implemented as a Telegram command/state transition in Phase 3; actual Codex execution still starts in Phase 4.

### `/reject`

- Purpose: reject a plan.
- Format: `/reject <task_id> [reason]`.
- Example: `/reject task-123 scope too broad`.
- Behavior: records rejection.
- Status: `waiting_plan_approval` -> `plan_rejected`.
- Errors: task not found, task not waiting for approval.
- Response: `task-123 rejected. Status: plan_rejected.`

Current phase note: implemented as a Telegram command/state transition in Phase 3.

### `/cancel`

- Purpose: cancel a task.
- Format: `/cancel <task_id>`.
- Example: `/cancel task-123`.
- Behavior: sets cancel flag; worker stops later stages at the nearest safe point.
- Status: current status -> `cancelled` if stopping is possible.
- Errors: task not found, already finished, cancellation unsafe at current step.
- Response: `task-123 cancellation requested.`

Current phase note: not implemented in Phase 1.

### `/help`

- Purpose: show commands.
- Format: `/help`.
- Behavior: sends short help.
- Status: implemented in the current Phase 1 slice.
- Errors: user not allowed.
- Response: command list and examples.

## Notifications

The initial minimal Phase 1 implementation now provides basic synchronous command responses over Telegram polling for accepted tasks and status lookups.

Current hotfix note:

- reply/send operations in the polling adapter now retry a small number of transient `TimedOut` failures before surfacing an error.

Later phases will add notifications for:

- `task accepted`: task created.
- `planning started`: Claude planning started.
- `plan ready`: plan saved.
- `approval required`: `/approve` or `/reject` required.
- `implementation started`: Codex started.
- `tests started`: build/test/lint started.
- `PR created`: PR created with link.
- `review blockers found`: blockers found, task moved to fix loop or `needs_fix`.
- `task ready`: task ready for human review.
- `task failed`: task failed with reason.

Current phase note:

- the bot can now approve or reject a plan after a worker/planner step has already moved the task into `waiting_plan_approval`;
- proactive Telegram notifications for planner results are still not implemented.

## Message Limits

- Do not send large logs in full.
- Do not send secrets.
- For long summaries, send a path or short excerpt.
- Inline buttons can be added after MVP; text commands are enough for the first launch.

## Startup

Phase 1 runtime entrypoints:

- `python -m ai_orchestrator.app --config <path> --database-path <path>`
- `ai-orchestrator --config <path> --database-path <path>`

Startup requirements:

- the bot token must be available in the environment variable named by `telegram.bot_token_env`;
- `telegram.allowed_user_ids` or the optional env override named by `telegram.allowed_user_ids_env` must include the operator's Telegram numeric user id;
- the SQLite database path can point to `data/tasks.sqlite3` for local smoke-tests.

Configuration follow-up:

- keep the bot token secret in environment or a deployment secret file;
- keep the allowlist configuration physically close to that secret-bearing deployment setup so operators manage Telegram access in one place.

Current local live-verification note:

- the repository entrypoint and startup path can be exercised locally;
- full Telegram API interaction still depends on working outbound network access plus a real bot token and allowed operator id.
