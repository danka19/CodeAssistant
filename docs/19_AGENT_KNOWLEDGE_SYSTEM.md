# 19 Agent Knowledge System

Date: 2026-05-23.
Status: active.

## Purpose

This document defines the knowledge-system model for CodeAssistant as a product capability, not just as a local repository documentation preference.

The system must support:

- future multi-agent work across multiple repositories;
- growth in agent count and role specialization;
- future services outside pure dev-orchestration, including personal-assistant style services;
- low-collision documentation updates by autonomous agents;
- clear source-of-truth retrieval for both humans and agents.

## Core Principles

The knowledge system uses these rules:

- atomic notes: one file, one concern;
- MOC or index notes: every major domain has an entrypoint map;
- ADR or decision notes: durable decisions are stored separately from discussion and plans;
- strong linking: summary files point to canonical files instead of duplicating them;
- status metadata: documents declare whether they are active, draft, deprecated, or archived;
- source of truth: every operational topic has one canonical file;
- state versus history separation: current state, plan, decisions, and logs stay in different files;
- service boundary separation: shared platform knowledge is separated from service-specific knowledge.

## Knowledge Domains

The product knowledge system should distinguish at least these domains:

- maps: where to find things;
- architecture: structural system design;
- runtime: behavior of orchestrated runtime agents;
- development: rules for contributors and local agents building the platform itself;
- decisions: accepted architectural or operational choices;
- plans: future and in-progress implementation work;
- state: current factual status of the platform or service;
- logs: append-only task and change history;
- runbooks: repeatable operational procedures;
- archive: deprecated or superseded material.

## Target Structure

Minimal target structure for CodeAssistant and future services:

```text
docs/
  maps/
  architecture/
  runtime/
  development/
  decisions/
  plans/
  state/
  logs/
  runbooks/
  archive/
```

For multi-service growth, the model must later support:

```text
docs/platform/
docs/services/codeassistant/
docs/services/personal-assistant/
```

MVP does not need the full service split yet, but the documentation must be written so that the split can happen without rewriting the knowledge model.

## Why This Is A Product Requirement

CodeAssistant is expected to orchestrate autonomous or semi-autonomous agents. Without an explicit knowledge system, the platform risks:

- agents reading stale or conflicting guidance;
- policy documents mixing runtime behavior and repository contribution rules;
- plans being mistaken for accepted decisions;
- logs being mistaken for current state;
- new services inheriting unsafe or irrelevant rules from dev-agent workflows.

The knowledge system is therefore part of product architecture and governance, not optional repo hygiene.

## Growth Rules

When new agents or services are added:

- each agent role must have a canonical role contract;
- each new service must get service-specific docs under a bounded namespace;
- handoff contracts must be documented explicitly;
- platform-wide policy stays separate from service-specific behavior;
- security domains must be documented separately when permissions differ;
- deprecated role behavior must point to the replacement source.

## Required Entry Documents

Each mature domain should expose one short map or entry file:

- `DOCS_MAP`
- `ARCHITECTURE_MAP`
- `RUNTIME_MAP`
- `DEVELOPMENT_MAP`
- `DECISION_INDEX`
- `PLAN_INDEX`
- `CURRENT_STATE`

These may start small in MVP and expand only when the volume justifies it.
