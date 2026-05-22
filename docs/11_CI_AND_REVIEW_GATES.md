# 11 CI And Review Gates

## CI For MVP

CI can be minimal. The key rule is that a PR must not be considered ready without a check report.

Minimal options:

- Python: `ruff`, `pytest`.
- Node: `npm test`, `npm run lint`, `npm run build`.
- C++/Qt: configure/build command, unit tests if present.
- Docs-only: markdown lint is optional, manual verification is acceptable.

If the project has no tests, the agent must explicitly write manual verification steps and include that in the PR.

## Review Gates

Required gates:

- Claude review.
- CI status or explicit record that CI is unavailable.
- Human review.
- Manual merge.

Optional gates:

- CodeRabbit PR review.
- GPT independent critic for high risk.
- Additional local smoke test.

## Ready Criteria

PR can receive status `ready_for_human` when:

- PR exists;
- diff matches the plan;
- unrelated files were not changed;
- build/test/lint ran or their unavailability is honestly documented;
- Claude review found no blockers;
- blockers were fixed or explicitly left for human decision;
- documentation/manual verification was updated when needed.

## Serious Blockers

Serious blockers:

- code does not build;
- tests fail;
- unrelated files changed;
- public API changed without approval;
- no check for a risky change;
- architecture violation;
- documentation loss;
- potential data deletion;
- unsafe commands;
- secrets in diff, prompt, or log;
- PR changes protected branch settings;
- implementation does not match the approved plan.

## Fix Loop

The MVP must limit the fix loop, for example to two attempts. If blockers remain, the task moves to `needs_fix` or `failed` with a clear reason and links to logs.

## Manual Merge

Even when CI and AI review pass, a human performs the merge. The agent can only prepare the PR and status `ready_for_human`.
