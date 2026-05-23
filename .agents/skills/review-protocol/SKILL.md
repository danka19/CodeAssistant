---
name: review-protocol
description: "Review completed work without editing it. Use when Codex is asked for review, risk assessment, regression checks, scope verification, missing-test analysis, or final diff inspection. Do not use when the requested task is to implement fixes directly."
---

# Review Protocol

Review output must lead with findings.

## Review Inputs

Require or reconstruct:
- task goal;
- scope and non-goals;
- changed files or diff;
- checks claimed;
- relevant docs or contracts.

If inputs are missing, state that in `residual_risks` or return `blocked` if review would be misleading.

Use the typed `ReviewReport` shape defined in project-local skill `team-handoff`.

Rules:
- Findings first, ordered by severity.
- Cite exact file and line where possible.
- Focus on correctness, regressions, security, missing tests, contract drift, and scope drift.
- Do not edit files while reviewing.
- If there are no findings, say so directly and list residual risk.

## Severity

- `P0`: breaks core behavior, data loss, security issue, or cannot ship.
- `P1`: likely bug/regression or missing required validation.
- `P2`: maintainability, test gap, unclear ownership, or medium-risk drift.
- `P3`: polish or low-risk cleanup.

## Verdicts

- `accept`: no blocking findings and checks are adequate.
- `accept_with_followups`: usable, but follow-up work should be tracked.
- `needs_fix`: specific fix needed before acceptance.
- `blocked`: missing decision, missing input, or unsafe uncertainty.
