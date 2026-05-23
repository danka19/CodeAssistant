# 00 Project Overview

## What We Are Building

AI Dev Orchestrator is a simple development agent system for a Linux VPS. The system accepts tasks from Telegram, creates a separate branch and git worktree, runs Claude for analysis and planning, runs Codex for implementation, executes checks, creates a GitHub Pull Request, and sends a report back to Telegram.

Final merge into `main` is always manual.

## Why We Are Building It

The goal is to get a practical workflow for small and medium development tasks without manually switching between Telegram, GitHub, CLI agents, worktrees, tests, and PRs. The system should save time on glue work, but it must not replace human architectural judgment or the final merge decision.

## Problems We Solve

- Context loss between task intake and implementation.
- Manual branch, worktree, log, and PR setup.
- Low visibility into CLI-agent work.
- No single task state.
- Weak reproducibility of agent runs.
- Risk of accidental changes in `main`.
- Need to receive status and PR links in a convenient channel.

## What Is In The MVP

- Telegram intake for new tasks.
- SQLite task database.
- `task_id` generation.
- Branch and git worktree creation.
- Claude planning step.
- `plan.md` persistence.
- Optional approval for medium/high-risk tasks.
- Codex implementation step.
- Log persistence.
- Build/test/lint execution when commands are configured.
- PR creation through GitHub CLI or GitHub API.
- Telegram report with status and PR link.
- CI and review gates.
- Manual merge.

## What Is Not In The MVP

- Large web UI.
- Kubernetes, Temporal, or a complex orchestrator.
- Devin-like platform.
- Multi-agent swarm.
- Voice input.
- Browser automation.
- Auto-deploy.
- Auto-merge.
- Life assistant.
- Payments and purchases.
- Complex cost analytics.

## Why GitHub-First

GitHub is already a durable source of truth for code, branches, PRs, CI, review, and protected branch rules. The MVP should use those existing mechanisms instead of duplicating them in a custom system.

GitHub-first gives us:

- understandable change history;
- standard PR and review flow;
- CI as a required gate;
- manual merge control;
- compatibility with CodeRabbit and other PR-review tools;
- ability to recover state even if the VPS worker fails.

## Why We Do Not Start With A Large Orchestrator

The first MVP must prove the workflow, not build an infrastructure platform. For one owner and a few repositories, a small Python worker, SQLite, git worktrees, GitHub CLI, and systemd are enough.

Docker Compose is not part of the first MVP. It can be reconsidered after Phase 7 if reproducible runtime or extra isolation becomes necessary.

A large orchestrator would add complexity before there are real scaling requirements: queues, retries, UI, distributed workers, tenancy, quotas, and complex observability.

## Why Dev-Agent And Life-Assistant Systems Should Stay Separate

The dev-agent system works with code, repositories, GitHub tokens, CI, and local commands. A life-assistant system may work with calendars, purchases, personal data, payments, and browsers. These are different security domains.

In the MVP they must be separate:

- separate secrets;
- separate permissions;
- separate approval gates;
- separate logs;
- separate risks;
- no dev-agent access to payments, production secrets, or personal integrations.

## Knowledge System As Product Infrastructure

CodeAssistant must also standardize how knowledge is stored and retrieved by agents.

This is a product requirement, not only a repository documentation preference.

The platform should evolve toward:

- atomic, single-topic documents;
- explicit source-of-truth files;
- separate current state, plans, decisions, logs, and policy;
- future service-specific knowledge boundaries;
- reliable agent retrieval with low ambiguity.

The active knowledge-system direction is defined in:

- `docs/19_AGENT_KNOWLEDGE_SYSTEM.md`
- `docs/20_DOCUMENTATION_OPERATIONS.md`
- `docs/21_PILOT_KNOWLEDGE_SYSTEM_PLAN.md`
