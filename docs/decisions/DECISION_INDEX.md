# Decision Index

Status: active
Audience: humans and coding agents
Owner: repository maintainers

## Purpose

This file routes readers to accepted durable decisions.

It is an index, not the full decision store.

## Current Canonical Decision Sources

- `docs/16_MVP_DECISIONS.md`
  Active omnibus record for chosen MVP decisions.
- `docs/16_MVP_DECISIONS.md#13-knowledge-system-decision`
  Accepted decision to adopt the repository Markdown based knowledge-system method.

## Supporting Decision Context

- `docs/19_AGENT_KNOWLEDGE_SYSTEM.md`
  Product-level design and operating model for the knowledge system. This is explanatory policy and architecture context, not the canonical accepted decision record.

## Migration Rule

Until the repository needs finer granularity, `docs/16_MVP_DECISIONS.md` remains the canonical accepted-decision source.

When split later:

- keep ADR-style decision files under `docs/decisions/`;
- update this index first;
- leave compatibility pointers from any superseded omnibus records.
