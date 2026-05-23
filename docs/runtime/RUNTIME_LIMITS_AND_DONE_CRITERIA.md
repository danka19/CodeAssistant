# Runtime Limits And Done Criteria

Status: active
Audience: future runtime agents and maintainers
Owner: repository maintainers
Update when: operational limits, approval gates, or acceptance rules change

## MVP Limits

- max concurrent Codex Implementers per repository: `1`
- max fix attempts per task: `2`
- max planner pass for a small or medium task: `1`
- high-risk work requires explicit approval
- model choice is configured by role, not chosen dynamically by the agent

If a limit is reached, the system should stop and return a clear status instead of continuing an uncontrolled loop.

## Git Rules

- Branch format: `agent/task-123-short-slug`
- Base branch: protected `main`
- All changes go through branch plus PR
- Direct push to `main` is forbidden
- Auto-merge is forbidden

PR content should include:

- goal;
- plan summary;
- changed files;
- tests and checks;
- documentation impact;
- risks;
- manual verification notes;
- AI review summary.

## Done Criteria

A runtime task may reach `ready_for_human` only when:

- a PR exists, or a non-coding result is explicitly stored;
- the diff matches the approved plan;
- unrelated files were not changed;
- checks ran, or their absence was explicitly documented;
- manual verification steps were recorded when automated tests are missing;
- the reviewer found no unhandled blockers;
- the summary artifact was written;
- the Telegram report was sent.

`ready_for_human` does not mean merge. Merge remains manual.
