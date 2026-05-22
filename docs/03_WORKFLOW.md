# 03 Workflow

## Общий workflow задачи

1. Пользователь отправляет задачу в Telegram.
2. Bot создает `task_id`, сохраняет input и ставит статус `created`.
3. Worker переводит задачу в `queued`, затем `planning`.
4. Repository manager обновляет base repo.
5. Worktree manager создает branch и worktree.
6. Claude runner создает план.
7. Если нужен approval, задача ждет `/approve` или `/reject`.
8. Codex runner реализует план.
9. Worker запускает build/test/lint, если они настроены.
10. Worker делает commit и push.
11. GitHub integration создает PR.
12. CI watcher и review runner проверяют результат.
13. При blockers запускается fix loop или задача переводится в `needs_fix`.
14. Notification service отправляет отчет и PR URL.
15. Human вручную review и merge.

## A. Small Task

Примеры: небольшой bugfix, документационный штрих, простая правка конфигурации, локальное исправление теста.

Особенности:

- Ручное подтверждение плана не требуется.
- Claude пишет короткий `plan.md`.
- Codex реализует сразу после planning.
- Обязательны git diff/status и доступные проверки.
- PR создается автоматически.
- Review gate остается обязательным, но может быть коротким.

Поток:

```text
/task
-> created
-> planning
-> short plan.md
-> implementing
-> testing
-> creating_pr
-> reviewing
-> ready_for_human
```

## B. Medium Task

Примеры: новая функция в существующем модуле, изменение workflow, правка нескольких файлов, миграция без высокого риска.

Особенности:

- Claude пишет полноценный `plan.md`.
- Пользователь подтверждает план через `/approve task-123`.
- Codex реализует только утвержденный план.
- Claude review обязателен.
- При blockers запускается Codex fix loop.
- PR создается после проверок и summary.

Поток:

```text
/task
-> planning
-> waiting_plan_approval
-> approved
-> implementing
-> testing
-> reviewing
-> needs_fix or creating_pr
-> ready_for_human
```

## C. Large/Risky Task

Примеры: архитектурное изменение, большой refactoring, изменение публичного API, C++/Qt многопоточность, внешние SDK, потенциальная потеря данных.

Особенности:

- Claude пишет `architecture_plan.md`.
- Пользователь подтверждает архитектурный план.
- Задача может быть разбита на несколько GitHub issues.
- Реализация идет по этапам.
- Каждый этап может иметь отдельную ветку или отдельный PR.
- Review gate строгий: CI, Claude review, optional independent critic, human review.
- Fix loop ограничен, чтобы не уйти в бесконечные правки.

Поток:

```text
/task
-> planning
-> architecture_plan.md
-> waiting_plan_approval
-> split into issues if needed
-> staged implementation
-> PR per stage
-> strict review
-> manual merge only
```

## Non-Coding Task Mode

Non-coding задачи не обязаны создавать implementation diff.

Типы:

- research;
- documentation;
- project planning;
- architecture analysis;
- monitoring;
- future life-assistant tasks.

Правила:

- Research должен сохранять `summary.md` и источники, если использовался внешний контекст.
- Documentation tasks могут создавать PR только с docs changes.
- Project planning должен явно отделять принятые решения от открытых вопросов.
- Monitoring после MVP лучше делать отдельным scheduled mode, а не смешивать с dev-agent loop.
- Future life-assistant tasks должны идти в отдельный security domain и не получать доступ к dev secrets.

