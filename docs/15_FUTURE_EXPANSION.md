# 15 Future Expansion

This document lists post-MVP extensions. These items must not enter the scope of the first MVP.

## Possible Improvements

- Web UI.
- Task dashboard.
- Cline Kanban.
- OpenHands smoke test.
- Voice input.
- Periodic tasks.
- Monitoring.
- Life-assistant as a separate boundary.
- Local models for classification.
- Multi-agent mode.
- Alternative implementation branches.
- GPT as independent critic.
- Support for multiple repositories.
- Support for multiple users.
- Jira/Linear integration.
- Deployment gates.

## Web UI

A web UI may replace part of the Telegram debug flow: task list, statuses, log links, approvals, filters. It is not needed for the MVP because Telegram plus GitHub are enough for the first end-to-end workflow.

## Task Dashboard

Useful after dozens of tasks exist. Until then, SQLite and Telegram `/status` are simpler.

## Cline Kanban

Can be used for visual task management if there is a steady task flow and a need for board view.

## OpenHands Smoke Test

Can become an additional validation layer, but must not be a required MVP dependency.

## Voice Input

Convenient for task intake, but adds speech-to-text, recognition errors, and security concerns. Post-MVP.

## Periodic Tasks And Monitoring

Scheduled checks can be added later: CI checks, stale PRs, dependency alerts. This is a separate mode, not the base task execution loop.

## Life Assistant

Must be a separate boundary:

- separate secrets;
- separate approvals;
- separate logs;
- no access to dev repo tokens unless necessary;
- separate risk model.

## Local Models For Classification

Cheap local models can be used for initial task classification, but simple rules and Claude planning are enough for the MVP.

## Multi-Agent Mode

Parallel agents, competition branches, or swarm mode should be added only after the single-agent workflow is stable.

## Alternative Implementation Branches

For complex tasks, the system can generate two solution variants in different branches and compare them. This may improve quality, but increases cost and complexity.

## GPT As Independent Critic

GPT can be used for independent critique of high-risk decisions, especially architecture, C++/Qt concurrency, SDK integrations, and large refactors.

## Multiple Repositories And Users

After MVP, add:

- repo registry;
- per-repo commands;
- per-user permissions;
- audit by user;
- quotas.

## Jira/Linear Integration

Can become a task source or status sync target. Not needed before the Telegram/GitHub loop is stable.

## Deployment Gates

Deploy must remain a separate post-MVP stage. It needs separate approvals, secrets, environments, rollback plan, and audit.
