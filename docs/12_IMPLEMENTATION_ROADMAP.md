# 12 Implementation Roadmap

## Phase 0 - Project Bootstrap

Goal: create the repository foundation and working rules.

Implement:

- create repository;
- add `AGENTS.md`;
- add baseline documentation;
- choose Python stack;
- configure `config/config.example.yaml`;
- prepare `README.md`.

Readiness criteria:

- docs describe the MVP path;
- agent rules exist;
- project structure is agreed;
- folder-first repository layout is in place;
- first PR can be reviewed manually.

Risks:

- scope too broad;
- mixing MVP and future expansion.

Do not do:

- production worker code;
- Kubernetes;
- complex UI.

## Phase 1 - Telegram Intake

Goal: accept tasks and store them.

Implement:

- Telegram bot;
- `/task`;
- `/status`;
- SQLite schema for tasks/events;
- allowed user id;
- basic notifications.

Readiness criteria:

- `/task` creates a task in SQLite;
- `/status task-123` returns state;
- unauthorized user is blocked.
- branch/worktree/planner/implementer steps are still out of scope.

Risks:

- incorrect long-message handling;
- secrets in config.

Do not do:

- worktree;
- Claude/Codex launch;
- inline UI.

## Phase 2 - GitHub/Repo Manager

Goal: prepare branch and worktree.

Implement:

- GitHub auth;
- repo clone/fetch;
- branch creation;
- git worktree;
- baseline logs;
- path safety checks.

Readiness criteria:

- task receives branch `agent/task-123-short-slug`;
- separate worktree is created;
- events record commands and exit codes.

Risks:

- stale base branch;
- branch name conflict;
- excessive token permissions.

Do not do:

- PR creation;
- agent implementation.

## Phase 3 - Claude Planning

Goal: get a plan before implementation.

Implement:

- run Claude for `plan.md`;
- save plan to `/runs/task-123/plan.md`;
- Telegram notification;
- approval for medium/high risk;
- `/approve` and `/reject`.

Readiness criteria:

- small task proceeds without approval;
- medium/high risk waits for approval;
- rejected plan is recorded.

Risks:

- overly generic plan;
- wrong risk classification.

Do not do:

- automatic high-risk implementation without approval;
- complex prompt management.

## Phase 4 - Codex Implementation

Goal: implement the approved plan.

Implement:

- run Codex using `plan.md`;
- save `implementation.log`;
- `git diff`;
- `git status`;
- run configured checks;
- commit.

Readiness criteria:

- Codex edits files only inside worktree;
- diff is saved in summary;
- commit is created in task branch.

Risks:

- unrelated changes;
- broken build;
- runaway agent.

Do not do:

- auto-push to `main`;
- silent test skip.

## Phase 5 - PR Creation

Goal: create PR and send the link.

Implement:

- push branch;
- `gh pr create`;
- PR template;
- labels;
- Telegram PR URL.

Readiness criteria:

- PR is created from feature branch into `main`;
- PR body contains plan/tests/risks/manual verification;
- Telegram receives the link.

Risks:

- auth failure;
- PR without useful description.

Do not do:

- merge;
- release/deploy.

## Phase 6 - CI/Review

Goal: check PR before human review.

Implement:

- wait for CI;
- Claude review;
- optional CodeRabbit status;
- needs_fix loop;
- review summary.

Readiness criteria:

- failed CI is not marked ready;
- blockers lead to fix loop or `needs_fix`;
- successful PR receives `ready_for_human`.

Risks:

- flaky CI;
- endless fix loop.

Do not do:

- require CodeRabbit as a mandatory MVP dependency;
- auto-approve.

## Phase 7 - MVP Hardening

Goal: make the MVP reliable for real use.

Implement:

- retries;
- cancellation;
- better logs;
- error handling;
- redaction;
- security checks;
- documentation updates;
- SQLite backup.

Readiness criteria:

- errors are understandable;
- task does not hang without status;
- logs are useful for debugging;
- security gates work.

Risks:

- complexity growth;
- attempt to turn MVP into a platform.

Do not do:

- distributed workers;
- web dashboard;
- life assistant;
- production deploy automation.

## Phase 8 - Knowledge System Rollout

Goal: make documentation reliable enough for multi-agent reuse across repositories and future services.

Implement:

- canonical knowledge domains for state, plans, decisions, logs, and policy;
- documentation update rules as part of task completion;
- pilot rollout on the CodeAssistant repository;
- review of ambiguity, duplication, and stale-doc risk;
- migration path toward multi-service documentation boundaries.

Done criteria:

- the product has a documented knowledge-system model;
- the current repository is used as a pilot proving ground;
- current state, plan, decision, and log responsibilities are defined;
- agents have explicit rules for documentation updates and evidence tracking.

Risks:

- over-engineering documentation before the workflow is proven;
- duplicating existing docs instead of reorganizing them cleanly;
- preserving too much history without clear active/deprecated markers.

Do not do:

- build a heavy documentation platform before the lightweight model is proven;
- require complex automation for every doc update in MVP;
- destroy or silently drop legacy information during reorganization.
