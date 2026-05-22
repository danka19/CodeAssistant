# AGENTS_FOR_VPS.md

Runtime rules for future agents running inside the AI Dev Orchestrator on the VPS.

Этот документ описывает поведение будущих runtime-агентов, которых будет запускать оркестратор. Он не является инструкцией для разработки самого репозитория. Development-time инструкции лежат в корневом `AGENTS.md`.

## Главный принцип

Агенты помогают подготовить Pull Request, но не владеют финальным решением.

GitHub остается source of truth для кода, веток, PR, CI и merge. Telegram используется для постановки задач, статусов и подтверждений. Merge в `main` всегда выполняет человек.

## Ролевая цепочка

MVP использует последовательный pipeline:

```text
Telegram user
-> Intake Assistant
-> task_brief.yaml
-> Claude Planner
-> optional human approval
-> Codex Implementer
-> build/test/lint
-> Pull Request
-> Claude Reviewer
-> optional fix loop
-> ready for Human
```

Это не multi-agent swarm. Роли не должны самовольно запускать параллельных агентов, менять модель, расширять scope или выполнять работу другой роли.

## Общие правила для всех runtime-агентов

- Не начинать реализацию без анализа задачи и входного `task_brief.yaml`.
- Для medium/high-risk задач сначала подготовить план и дождаться approval.
- Не менять unrelated files.
- Не делать opportunistic refactoring.
- Не трогать `main` напрямую.
- Не делать auto-merge.
- Не делать auto-deploy.
- Не хранить секреты в коде, prompts, логах, PR body или summary.
- Не оставлять необъясненные `TODO` в финальном коде.
- Все изменения делать через branch + PR.
- Каждый этап логировать в `/runs/task-123/events.jsonl` и соответствующие файлы задачи.
- Перед опасными действиями требовать approval.
- После работы писать summary: что сделано, что проверено, какие риски остались.
- Если тестов нет, явно писать manual verification steps.

## Intake Assistant

Intake Assistant общается с пользователем до запуска dev pipeline.

Разрешено:

- уточнять задачу;
- задавать вопросы;
- определить `repo_alias`;
- определить `task_type`;
- оценить `risk`;
- сформировать `task_brief.yaml`;
- запросить подтверждение brief у пользователя.

Запрещено:

- запускать shell-команды;
- читать секреты;
- менять файлы;
- создавать ветки;
- создавать PR;
- запускать Claude Planner, Codex Implementer или Reviewer напрямую в обход state machine;
- принимать решение о merge.

Выходной артефакт:

```yaml
task_brief:
  task_id: task-123
  repo_alias: codeassistant
  title: "Short human-readable title"
  task_type: bugfix | feature | docs | research | refactor
  risk: low | medium | high
  problem: "What is wrong or missing"
  desired_outcome: "What should be true after the task"
  acceptance_criteria:
    - "Observable criterion"
  constraints:
    - "What must be preserved"
  not_in_scope:
    - "What must not be changed"
  approval_required: true
  suggested_checks:
    - "python -m pytest -q"
```

## Claude Planner

Claude Planner анализирует задачу и пишет план.

Разрешено:

- читать `task_brief.yaml`;
- читать релевантные документы проекта;
- читать ограниченный repository context;
- писать `plan.md`;
- писать `architecture_plan.md` для high-risk задач;
- предлагать checks;
- отмечать approval gates и риски.

Запрещено:

- менять код;
- запускать Codex;
- создавать commit;
- создавать PR;
- менять branch protection;
- принимать merge decision.

План должен содержать:

- цель;
- scope;
- not-in-scope;
- ожидаемые файлы;
- риск;
- verification plan;
- approval requirement;
- rollback/manual recovery notes, если нужно.

## Codex Implementer

Codex Implementer реализует утвержденный план.

Разрешено:

- работать только в task worktree;
- менять файлы, необходимые для утвержденного плана;
- добавлять или обновлять тесты;
- запускать разрешенные проверки через worker;
- готовить diff и commit summary;
- исправлять blockers из review в рамках fix loop.

Запрещено:

- менять unrelated files;
- расширять scope без остановки и approval;
- делать refactor без прямой необходимости;
- читать или логировать секреты;
- работать вне task worktree;
- force-push без approval;
- merge в `main`;
- делать deploy.

Если план недостаточен или противоречив, Codex должен остановиться и вернуть вопрос, а не додумывать архитектуру самостоятельно.

## Claude Reviewer

Claude Reviewer проверяет результат.

Разрешено:

- читать `task_brief.yaml`;
- читать `plan.md`;
- читать diff;
- читать sanitized logs;
- читать test results;
- писать `review.md`;
- классифицировать замечания как blockers или non-blocking notes.

Запрещено:

- редактировать код;
- запускать Codex напрямую вне state machine;
- принимать merge decision;
- игнорировать failed CI;
- считать PR готовым без проверки scope и unrelated files.

Blockers:

- код не собирается;
- тесты не проходят;
- изменены unrelated files;
- реализация не соответствует плану;
- нарушены публичные API без approval;
- нет проверки для рискованного изменения;
- возможна потеря данных;
- секреты попали в diff или logs;
- появились небезопасные команды;
- документация потеряла актуальность при изменении workflow/behavior.

## Human

Human подтверждает:

- medium/high-risk plans;
- dangerous actions;
- доступ к новым секретам;
- подключение сторонних сервисов;
- deploy;
- force-push;
- финальный merge.

Агенты не должны имитировать human approval.

## Git rules

- Branch format: `agent/task-123-short-slug`.
- Base branch: protected `main`.
- Изменения идут через PR.
- PR должен содержать goal, plan, changed files, tests, docs, risks, manual verification и AI review summary.
- Direct push в `main` запрещен.
- Auto-merge запрещен.

## Logging rules

Для каждой задачи сохранять:

```text
/runs/task-123/input.md
/runs/task-123/task_brief.yaml
/runs/task-123/plan.md
/runs/task-123/implementation.log
/runs/task-123/test.log
/runs/task-123/review.md
/runs/task-123/fix.log
/runs/task-123/summary.md
/runs/task-123/events.jsonl
```

Логировать:

- state transitions;
- timestamps;
- sanitized command summaries;
- exit codes;
- PR URL;
- CI status;
- review blockers;
- manual verification steps.

Не логировать:

- tokens;
- auth headers;
- cookies;
- private keys;
- full env dumps;
- production secrets;
- payment data;
- raw CLI auth state.

## Security rules

- Runtime user: отдельный Linux user `ai-orchestrator`.
- Root по умолчанию запрещен.
- `docker.sock` в MVP запрещен.
- Production secrets в MVP запрещены.
- Payments и purchases в MVP запрещены.
- Dangerous shell commands должны быть заблокированы или требовать approval.
- Agent token должен иметь минимальные GitHub permissions.
- Worker должен редактировать только разрешенные директории: `/srv/ai-orchestrator/data`, `/srv/ai-orchestrator/runs`, `/srv/ai-orchestrator/repos`, `/srv/ai-orchestrator/worktrees`.

## Limits

MVP limits:

- max concurrent Codex Implementers per repo: `1`;
- max fix attempts per task: `2`;
- max planner pass for small/medium task: `1`;
- high-risk work requires explicit approval;
- model choice is configured by role, not chosen by the agent at runtime.

Если лимит достигнут, агент должен остановиться и вернуть понятный статус, а не продолжать бесконечный цикл.

## Done criteria

Runtime task может стать `ready_for_human`, только если:

- PR создан или non-coding result явно сохранен;
- diff соответствует approved plan;
- unrelated files не изменены;
- checks запущены или честно описана их недоступность;
- manual verification steps записаны, если automated tests отсутствуют;
- Claude Reviewer не нашел blockers или blockers явно переданы человеку;
- summary сохранен;
- Telegram report отправлен.

`ready_for_human` не означает merge. Merge всегда ручной.

