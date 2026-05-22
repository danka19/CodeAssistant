# Documentation Standard

Status: active
Audience: humans and coding agents
Owner: repository maintainers
Update when: documentation workflow, file layout, or writing conventions change

## Goal

Documentation in this repository must be easy for both humans and AI agents to navigate, trust, and update safely. The system must reduce ambiguity, duplication, and context sprawl.

## Core Rules

1. One file, one job.
   A document should explain one subject: scope, architecture, runtime policy, logging, or one other clearly bounded topic.

2. Short entrypoints, detailed leaf documents.
   Root-level files should orient and route. Deep detail belongs in topical files.

3. Clear source of truth.
   Every important subject should have one canonical file. Summary files must link to that source instead of restating everything.

4. Development-time and runtime policy stay separate.
   Rules for contributors in this repository must not be mixed with the future behavior of orchestrated VPS agents.

5. Present decisions separately from options.
   Decision records should capture chosen direction. Exploratory ideas belong in roadmap, risks, or future-expansion documents.

6. Preserve MVP boundaries.
   MVP behavior, future ideas, and rejected scope must not be blended in one section.

7. Optimize for diffability.
   Prefer small sections, explicit headings, flat lists, and stable filenames so changes are easy to review.

8. State update triggers.
   Policy documents should say when they need to be revised.

## Recommended Folder System

Use this structure for all new documentation work:

- `docs/README.md`
  Main map and source-of-truth index.
- `docs/governance/`
  Documentation standards, doc ownership, refactor plans, and maintenance policy.
- `docs/development/`
  Instructions for humans and coding agents working on this repository.
- `docs/runtime/`
  Rules for the future AI Dev Orchestrator runtime roles and artifacts.
- `docs/decisions/`
  Future home for split decision records when `docs/16_MVP_DECISIONS.md` is decomposed.
- `docs/specs/`
  Future home for deep component specs when current numbered specs become too large.

The existing numbered files remain valid source material. New governance and policy work should use semantic folders and names.

## File Template

Every new policy or governance document should start with a small metadata block:

```text
Status: active | draft | deprecated
Audience: humans | coding agents | runtime agents
Owner: repository maintainers
Update when: short trigger description
```

Then keep this order:

1. Purpose
2. Scope
3. Rules or decisions
4. Links to related source documents

## Naming Conventions

- Use semantic uppercase snake case for policy and standards:
  `DEVELOPMENT_AGENT_POLICY.md`
  `RUNTIME_LOGGING_AND_SECURITY.md`
- Use nouns, not vague verbs.
- Avoid version numbers in filenames unless the file is a real versioned artifact.
- Avoid `misc`, `notes`, `guide2`, and similar low-signal names.

## Decomposition Triggers

Split a document when any of these becomes true:

- it contains more than one operational domain;
- readers need different audiences for different sections;
- sections are frequently updated by unrelated changes;
- the file acts as both a summary and a deep spec;
- the document becomes the only place where several policies are hidden together.

## AI-Agent Writing Rules

- State what the file is for in the first paragraph.
- Use stable headings that can be referenced in prompts and reviews.
- Prefer explicit constraints over prose that implies them.
- Avoid duplicating the same rules in multiple policy files.
- When summarizing another file, link to it and keep the summary intentionally shorter.
- When a file is superseded, replace it with a short compatibility stub that points to the new canonical location.

## Current Refactor Direction

This repository is adopting:

- `AGENTS.md` as a short repository entrypoint only;
- detailed development rules in `docs/development/`;
- detailed runtime rules in `docs/runtime/`;
- an indexed docs system rooted at `docs/README.md`.
