# 21 Pilot Knowledge System Plan

Status: active.
Audience: humans and coding agents
Owner: repository maintainers
Update when: the repository pilot rollout strategy or success criteria change

Date: 2026-05-23.

## Purpose

This document plans the pilot rollout of the knowledge-system model on the current CodeAssistant repository.

The current repository is the first proving ground before the same model is used by runtime agents across other repositories and services.

## Pilot Goals

- test whether agents can find canonical docs faster;
- reduce policy duplication and mixed-topic documents;
- make current state, decisions, plans, and logs distinct;
- find the smallest documentation process that remains reliable under agent work;
- preserve existing information while reorganizing it.

## Scope Of The Pilot

The pilot should introduce and validate:

- docs maps or entrypoints;
- canonical policy files;
- separated knowledge domains;
- a state-tracking layer;
- a task-log convention;
- compatibility stubs for superseded docs when needed.

The pilot should not:

- rewrite the entire repository into a heavy wiki;
- create a large automation subsystem before workflows are proven;
- discard older information without replacement pointers.

## Minimal Rollout Steps

1. Add the knowledge-system policy docs and source-of-truth map.
2. Shorten overloaded entrypoint files.
3. Split mixed development and runtime policy where needed.
4. Introduce state and log targets for the repository.
5. Define how future task completion must update docs.
6. Review the resulting structure for ambiguity and collisions.

## Pilot Success Criteria

The pilot is successful when:

- an agent can determine the canonical file for a topic quickly;
- current state can be found without reading task history;
- logs do not masquerade as policy;
- policy does not masquerade as implementation status;
- repo contributors can update docs with low ambiguity after a task;
- existing important information remains reachable after reorganization.

## Review Focus

The pilot review should explicitly assess:

- missing links between canonical docs;
- contradictory instructions;
- places where state is still implicit;
- whether the system is still too heavy for MVP;
- whether service-level growth is supported without early over-engineering.
