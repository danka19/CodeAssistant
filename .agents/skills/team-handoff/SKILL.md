---
name: team-handoff
description: "Create compact typed handoffs for project subagent work. Use whenever the root assistant prepares a WorkOrder for analyst_architect, programmer, reviewer, or verifier, or when consuming AgentResult, ReviewReport, or VerificationResult. Do not use for normal implementation details unless a delegation boundary, review boundary, or verification boundary is involved."
---

# Team Handoff

Use typed, compact handoffs.

## Principles

- Pass only task-local context.
- Do not pass full chat history.
- Prefer file paths, commands, and constraints over prose.
- Include non-goals so roles do not merge.
- Make stop conditions explicit.

## TaskBrief

Use this before splitting work:

```text
TaskBrief
user_goal:
approved_scope:
non_goals:
known_context:
unknowns:
success_criteria:
```

## WorkOrder

```text
WorkOrder
role:
goal:
scope:
non_goals:
read_paths:
write_paths:
allowed_tools:
required_output:
stop_conditions:
token_budget:
```

Field rules:
- `role`: one of `analyst_architect`, `programmer`, `reviewer`, `verifier`.
- `scope`: positive work to do.
- `non_goals`: adjacent work to avoid.
- `read_paths`: exact files or narrow directories.
- `write_paths`: empty for read-only roles.
- `allowed_tools`: shell/search/apply_patch/etc. if relevant.
- `required_output`: exact result shape.
- `stop_conditions`: when to return blocked.
- `token_budget`: small | medium | large.

## AgentResult

```text
AgentResult
status: done | blocked | needs_fix | not_started
summary:
files_read:
files_changed:
checks_run:
findings:
risks:
handoff_notes:
needs_user_decision:
```

## ReviewReport

```text
ReviewReport
verdict: accept | accept_with_followups | needs_fix | blocked
findings:
residual_risks:
checks_reviewed:
missing_checks:
scope_notes:
```

## VerificationResult

```text
VerificationResult
commands_run:
passed:
failed:
skipped:
not_run:
evidence_summary:
likely_failure_area:
```

Rules:
- Keep summaries under 200 tokens unless detail is requested.
- Do not paste full files.
- Include exact paths and commands.
- Mark uncertainty explicitly.
- If blocked, state the smallest safe next action.
