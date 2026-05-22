# 14 Risks And Limitations

## Risks

| Risk | Probability | Impact | Mitigation | What To Do In MVP |
|---|---:|---:|---|---|
| Claude/ChatGPT subscriptions may not fit service automation | Medium | High | Check terms of use and CLI auth model | Keep runner replaceable, do not bind the system to one auth method |
| API billing may be needed later | Medium | Medium | Separate runner interface from billing/auth | Track usage manually or through simple logs without complex cost analytics |
| Limits may run out | High | Medium | Timeouts, retries, clear failed state | On limit failure, set `failed` with reason and allow manual retry |
| Agents may produce an incorrect diff | High | High | Plan, diff review, CI, Claude review, human merge | Do not consider PR ready without review gates |
| Agent may overcomplicate the solution | Medium | Medium | Scope control, no opportunistic refactoring | Forbid unrelated refactor in `AGENTS.md` |
| CI may be missing | Medium | Medium | Manual verification required | Explicitly record missing CI and steps |
| C++/Qt projects may need a specific local environment | Medium | High | Repo-specific setup docs, prepared VPS image | Start MVP with one test repository with a clear environment |
| GUI checks are hard to automate on VPS | High | Medium | Headless tests, manual verification, screenshots later only | Do not include GUI automation in MVP |
| Secrets and tokens require caution | High | High | Redaction, scoped tokens, env secrets | Forbid secrets in prompts/logs/code |
| Telegram may be insufficient for complex debugging | Medium | Medium | Store full logs on disk, short Telegram status | Use Telegram only for commands/status; debug through VPS/GitHub |
| Worker may hang on subprocess | Medium | Medium | Timeouts, process groups, cancellation | Add timeout for agent/test commands |
| Worktree may remain dirty after failure | Medium | Medium | Per-task worktree, status checks, cleanup policy | Do not reuse worktrees between tasks |
| Review loop may become endless | Medium | Medium | Limit attempts | Limit fix attempts |
| GitHub token may be too broad | Medium | High | Scoped token or GitHub App | Minimal permissions, protected main |
| Risk classification may be wrong | Medium | Medium | Human approval for ambiguous tasks | When unsure, treat as medium/high |

## MVP Limitations

- One VPS.
- One worker process.
- One or more preconfigured repo aliases.
- Telegram as a simple command interface.
- SQLite instead of an external database.
- No web dashboard.
- No auto-deploy.
- No auto-merge.
- No production secrets.
- No payments.
- No browser automation.

## Risk Response Principle

If an action may damage code, data, security, or money, the MVP must stop and request approval. If approval flow is not implemented yet for that action, the task must end with clear `failed` or `waiting_approval` status.
