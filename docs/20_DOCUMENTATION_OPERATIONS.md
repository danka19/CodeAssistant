# 20 Documentation Operations

Date: 2026-05-23.
Status: active.

## Purpose

This document defines how documentation is updated, validated, and kept trustworthy during agent work.

## Canonical Document Types

Do not mix these concerns in one file:

- current state: what is true now;
- plan: what is intended next;
- decision: what has been chosen and why;
- log: what happened and when;
- runbook: how to perform a repeatable procedure;
- policy: what is allowed or required;
- architecture: how the system is structured.

## After-Task Update Rule

After every completed task, the responsible agent or worker stage must evaluate documentation impact.

If the task changed:

- behavior;
- architecture;
- workflow;
- role boundaries;
- state transitions;
- configuration surface;
- security constraints;
- operational process;

then the canonical document for that topic must be updated in the same task.

If no documentation update is required, the task summary must state that explicitly and why.

## Required Post-Task Checks

Every task close-out should answer:

- did current state change;
- did accepted design or policy change;
- did a new durable decision get made;
- did runbook or operator procedure change;
- did the task produce evidence worth logging.

This yields the required actions:

- current state changed -> update the canonical state file;
- design or policy changed -> update the canonical spec or policy file;
- durable decision made -> add or update a decision record;
- task completed -> add a task log entry;
- workflow or procedure changed -> update the relevant runbook.

## State Tracking Model

Current project truth must not be reconstructed from random docs.

The target model is:

- one canonical `CURRENT_STATE.md` for factual status;
- one canonical plan index or roadmap for forward work;
- one decision index for accepted choices;
- append-only task logs for execution history.

State is curated and rewritten.
Logs are append-only and historical.
Decisions are durable.
Plans are provisional until accepted.

## Evidence And Completion

A task step should not be marked complete only because files changed.

Each meaningful step should define:

- status: `planned`, `in_progress`, `blocked`, `done`;
- done criteria;
- evidence.

Typical evidence:

- commit hash;
- PR URL;
- test or check result;
- updated state doc;
- updated decision record;
- updated task log.

## Logging Policy

Use layered logs:

- decision log: durable ADR-style decisions;
- task log: append-only operational history per task;
- state snapshot: curated present-tense summary.

Task logs should record at least:

- task id;
- date;
- actor or stage;
- summary;
- docs updated;
- checks run;
- result;
- evidence links;
- open follow-ups.

## Agent Retrieval Rules

To reduce collisions and stale reads:

- each important topic must have one canonical file;
- summary files must link to the canonical file;
- deprecated docs must point to replacements;
- log files must never be treated as source of truth for policy or current state;
- plans must not be used as evidence that behavior is already implemented.

## Minimum Viable Enforcement

MVP does not need a complex doc-management subsystem.

It does need:

- explicit documentation update responsibility in task completion;
- stable canonical files;
- append-only task logging;
- visible current state tracking;
- clear separation between policy, state, decisions, and logs.
