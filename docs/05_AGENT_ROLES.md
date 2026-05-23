# 05 Agent Roles

## Claude

Claude is used as planner, architect, and reviewer.

Responsibilities:

- task analysis;
- documentation review;
- architecture planning;
- writing `plan.md`;
- writing `architecture_plan.md` for large/risky tasks;
- writing `review.md`;
- finding blockers;
- checking whether implementation matches the plan;
- estimating task risk.

Must not:

- edit code in the MVP;
- merge;
- expose secrets in prompts/logs;
- make the final decision instead of a human.

## Codex

Codex is used as implementer.

Responsibilities:

- implement the approved `plan.md`;
- edit files in the task worktree;
- add or update tests;
- fix review findings;
- prepare diff;
- write commit summary;
- update documentation/changelog when needed.

Must not:

- expand scope without cause;
- edit unrelated files;
- do opportunistic refactoring;
- bypass approval;
- merge into `main`.

## CodeRabbit

CodeRabbit is used as an additional PR-review layer.

Responsibilities:

- additional PR review;
- finding obvious errors;
- PR comments;
- highlighting possible regressions.

Constraints:

- not the main architecture reviewer;
- does not replace Claude review;
- does not replace human review;
- does not make merge decisions.

## Human

The human remains the owner of the final decision.

Responsibilities:

- approves large plans;
- makes final decisions on disputed questions;
- merges PRs;
- grants new access;
- approves dangerous actions;
- decides when to expand the MVP.

## GPT As Independent Critic

GPT is useful as an independent critic when the cost of error is high or a second architecture opinion is needed.

Examples:

- complex architecture;
- disputed decision;
- large refactor;
- C++/Qt concurrency;
- external SDK integrations;
- data migrations;
- security-sensitive changes;
- high cost of error.

GPT must not become a required gate for every MVP task. It should be enabled selectively for medium/high-risk tasks.

## Agent Knowledge Responsibilities

Every role that changes the system must preserve knowledge integrity.

Minimum responsibilities:

- planners point to canonical policy and architecture docs;
- implementers update documentation when behavior or workflow changes;
- reviewers check whether documentation drift was introduced;
- human operators verify that durable decisions were not left only in task history.

Knowledge-system rules are defined in:

- `docs/19_AGENT_KNOWLEDGE_SYSTEM.md`
- `docs/20_DOCUMENTATION_OPERATIONS.md`
