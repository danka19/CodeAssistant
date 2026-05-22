# 12 Implementation Roadmap

## Phase 0 - Project Bootstrap

Цель: создать основу репозитория и правила работы.

Реализовать:

- создать репозиторий;
- добавить `AGENTS.md`;
- добавить базовую документацию;
- выбрать Python stack;
- настроить `config.example.yaml`;
- подготовить `README.md`.

Критерии готовности:

- docs описывают MVP path;
- есть правила для агентов;
- структура проекта согласована;
- первый PR можно review вручную.

Риски:

- слишком широкий scope;
- смешение MVP и future expansion.

Не делать:

- production-код worker;
- Kubernetes;
- сложный UI.

## Phase 1 - Telegram Intake

Цель: принимать задачи и сохранять их.

Реализовать:

- Telegram bot;
- `/task`;
- `/status`;
- SQLite schema для tasks/events;
- allowed user id;
- базовые notifications.

Критерии готовности:

- `/task` создает task в SQLite;
- `/status task-123` возвращает состояние;
- unauthorized user блокируется.

Риски:

- неправильная обработка длинных сообщений;
- секреты в config.

Не делать:

- worktree;
- запуск Claude/Codex;
- inline UI.

## Phase 2 - GitHub/Repo Manager

Цель: подготовить branch и worktree.

Реализовать:

- GitHub auth;
- repo clone/fetch;
- branch creation;
- git worktree;
- базовые логи;
- path safety checks.

Критерии готовности:

- task получает branch `agent/task-123-short-slug`;
- создается отдельный worktree;
- events фиксируют команды и exit codes.

Риски:

- stale base branch;
- конфликт имен веток;
- лишние permissions у токена.

Не делать:

- PR creation;
- agent implementation.

## Phase 3 - Claude Planning

Цель: получить план до реализации.

Реализовать:

- запуск Claude для `plan.md`;
- сохранение plan в `/runs/task-123/plan.md`;
- Telegram notification;
- approval для medium/high risk;
- `/approve` и `/reject`.

Критерии готовности:

- small task идет дальше без approval;
- medium/high risk ждет approval;
- rejected plan фиксируется.

Риски:

- слишком общий план;
- неверная risk classification.

Не делать:

- автоматическую реализацию high risk без approval;
- сложный prompt management.

## Phase 4 - Codex Implementation

Цель: реализовать утвержденный план.

Реализовать:

- запуск Codex по `plan.md`;
- сохранение `implementation.log`;
- `git diff`;
- `git status`;
- запуск configured checks;
- commit.

Критерии готовности:

- Codex меняет файлы только в worktree;
- diff сохраняется в summary;
- commit создается в task branch.

Риски:

- unrelated changes;
- broken build;
- runaway agent.

Не делать:

- auto-push в `main`;
- silent test skip.

## Phase 5 - PR Creation

Цель: создать PR и отправить ссылку.

Реализовать:

- push branch;
- `gh pr create`;
- PR template;
- labels;
- Telegram PR URL.

Критерии готовности:

- PR создается из feature branch в `main`;
- PR body содержит plan/tests/risks/manual verification;
- Telegram получает ссылку.

Риски:

- auth failure;
- PR без полезного описания.

Не делать:

- merge;
- release/deploy.

## Phase 6 - CI/Review

Цель: проверить PR перед human review.

Реализовать:

- ожидание CI;
- Claude review;
- optional CodeRabbit status;
- needs_fix loop;
- review summary.

Критерии готовности:

- failed CI не помечается ready;
- blockers ведут к fix loop или `needs_fix`;
- успешный PR получает `ready_for_human`.

Риски:

- flaky CI;
- бесконечный fix loop.

Не делать:

- требовать CodeRabbit как обязательный dependency MVP;
- auto-approve.

## Phase 7 - MVP Hardening

Цель: сделать MVP устойчивым для реального использования.

Реализовать:

- retries;
- cancellation;
- better logs;
- error handling;
- redaction;
- security checks;
- documentation updates;
- backup для SQLite.

Критерии готовности:

- понятные ошибки;
- task не зависает без статуса;
- logs пригодны для debug;
- security gates работают.

Риски:

- рост сложности;
- попытка превратить MVP в платформу.

Не делать:

- distributed workers;
- web dashboard;
- life assistant;
- production deploy automation.

