# 06 Telegram Bot Spec

## Purpose

The Telegram bot is the main user interface for the MVP. It accepts tasks, shows status, returns short logs, and accepts approvals.

For the MVP, one allowed Telegram user id is sufficient.

## Commands

### `/task`

- Purpose: create a new task.
- Format: `/task <repo_alias> <task description>`.
- Example: `/task codeassistant Fix crash when camera window closes`.
- Behavior: creates `task_id`, stores input, sets status `created`.
- Status: `created` -> `queued`.
- Errors: unknown repo alias, empty description, unauthorized user, database unavailable.
- Response: `Task task-123 accepted. Status: queued.`

### `/status`

- Purpose: show task state.
- Format: `/status <task_id>`.
- Example: `/status task-123`.
- Behavior: reads SQLite and returns status, branch, PR URL, latest event.
- Status: unchanged.
- Errors: task not found, user not allowed.
- Response: `task-123: implementing. Branch: agent/task-123-fix-camera-close.`

### `/log`

- Purpose: show recent task log lines.
- Format: `/log <task_id>`.
- Example: `/log task-123`.
- Behavior: returns a tail from `events.jsonl` and key logs.
- Status: unchanged.
- Errors: task not found, logs unavailable, log too large.
- Response: short secret-free fragment.

### `/approve`

- Purpose: approve a plan or gated action.
- Format: `/approve <task_id>`.
- Example: `/approve task-123`.
- Behavior: records an approval event.
- Status: `waiting_plan_approval` -> `implementing` or `queued`.
- Errors: task not found, task not waiting for approval, user not allowed.
- Response: `task-123 approved. Implementation will start.`

### `/reject`

- Purpose: reject a plan.
- Format: `/reject <task_id> [reason]`.
- Example: `/reject task-123 scope too broad`.
- Behavior: records rejection.
- Status: `waiting_plan_approval` -> `plan_rejected`.
- Errors: task not found, task not waiting for approval.
- Response: `task-123 rejected. Reason saved.`

### `/cancel`

- Purpose: cancel a task.
- Format: `/cancel <task_id>`.
- Example: `/cancel task-123`.
- Behavior: sets cancel flag; worker stops later stages at the nearest safe point.
- Status: current status -> `cancelled` if stopping is possible.
- Errors: task not found, already finished, cancellation unsafe at current step.
- Response: `task-123 cancellation requested.`

### `/help`

- Purpose: show commands.
- Format: `/help`.
- Behavior: sends short help.
- Status: unchanged.
- Errors: none.
- Response: command list and examples.

## Notifications

The MVP must send notifications for:

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

## Message Limits

- Do not send large logs in full.
- Do not send secrets.
- For long summaries, send a path or short excerpt.
- Inline buttons can be added after MVP; text commands are enough for the first launch.
