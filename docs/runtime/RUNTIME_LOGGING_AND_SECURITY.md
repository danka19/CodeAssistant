# Runtime Logging And Security

Status: active
Audience: future runtime agents and maintainers
Owner: repository maintainers
Update when: runtime logging, storage, or security controls change

## Logging Rules

For each task, persist artifacts in the task run directory:

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
- full environment dumps;
- production secrets;
- payment data;
- raw CLI auth state.

## Security Rules

- Runtime user: dedicated Linux user `ai-orchestrator`.
- Root use is forbidden by default.
- `docker.sock` is forbidden in MVP.
- Production secrets are forbidden in MVP.
- Payments and purchases are forbidden in MVP.
- Dangerous shell commands must be blocked or require approval.
- Agent GitHub credentials must use minimal permissions.
- Worker writes must stay inside:
  - `/srv/ai-orchestrator/data`
  - `/srv/ai-orchestrator/runs`
  - `/srv/ai-orchestrator/repos`
  - `/srv/ai-orchestrator/worktrees`
