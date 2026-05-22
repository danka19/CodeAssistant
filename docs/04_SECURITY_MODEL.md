# 04 Security Model

## Baseline Model

The MVP runs on a Linux VPS under a separate unprivileged user, for example `ai-orchestrator`. The agent system must not have root access by default and must not have access to production secrets, payments, purchases, or dangerous system actions.

## Required Constraints

- Separate Linux user for the agent.
- No root by default.
- No `docker.sock` in the MVP.
- Scoped GitHub token or GitHub App.
- Protected `main`.
- Required PR review.
- Required status checks.
- No auto-merge.
- Do not store secrets in prompts, logs, PR body, or code.
- Store Telegram bot token in env/secrets.
- Do not log OpenAI/Anthropic auth.
- Dangerous shell commands must be blocked or require approval.
- Payments, purchases, and production deploy are not part of the MVP.

## Secrets

Allowed storage:

- systemd environment file with `600` permissions;
- `.env` outside git for local development only;
- secret manager after MVP.

Forbidden:

- committing secrets;
- writing tokens to `/runs`;
- printing the full `env`;
- injecting auth headers into prompts;
- passing production credentials to agents.

## GitHub Security

- `main` is protected.
- Direct push to `main` is forbidden.
- Merge is manual only.
- Required checks must match the real project CI.
- Agent token must have minimum required permissions:
  - read/write contents for feature branches;
  - pull requests write;
  - checks/status read;
  - issues write, optional.
- Repository administration settings must not be changed by the worker without separate approval.

## Dangerous Commands

The MVP must block or require approval for commands that:

- delete files recursively;
- change system directories;
- run `sudo`;
- change firewall/users/ssh;
- access `docker.sock`;
- deploy;
- rewrite git history;
- force-push without permission;
- read arbitrary secret files.

## Approval Gates

Required approval gates:

- Plan for a large or risky task.
- PR creation when the task is marked high risk.
- Re-run after blocker review if the fix may change architecture.
- Merge.
- Deploy.
- Access to new secrets.
- Third-party service connection.
- Security setting changes.
- Force push.

## MVP Policy

In the MVP it is better to refuse an action than to give an agent broad access. If a task requires root, production secrets, payments, auto-deploy, or external services, the worker must move the task to `failed` or `waiting_approval` with a clear explanation.
