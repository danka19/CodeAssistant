# 09 Task States

## State machine

```text
created
-> queued
-> planning
-> waiting_plan_approval
-> implementing
-> testing
-> creating_pr
-> reviewing
-> needs_fix
-> fixing
-> testing
-> reviewing
-> ready_for_human
-> done
```

Terminal states:

```text
done
failed
cancelled
plan_rejected
```

## Статусы

| Status | Что значит | Кто переводит | Следующие статусы | Данные |
|---|---|---|---|---|
| `created` | Task принят bot | Bot | `queued`, `cancelled` | input, user_id, repo_alias |
| `queued` | Task ждет worker | Bot/Worker | `planning`, `cancelled`, `failed` | task_id, priority, created_at |
| `planning` | Claude готовит план | Worker | `waiting_plan_approval`, `implementing`, `failed`, `cancelled` | branch, worktree, planning log |
| `waiting_plan_approval` | Нужен approval | Worker | `implementing`, `plan_rejected`, `cancelled` | plan path, approval request |
| `plan_rejected` | План отклонен | Bot/Human | terminal | rejection reason |
| `implementing` | Codex реализует | Worker | `testing`, `failed`, `cancelled` | implementation log, changed files |
| `testing` | Worker запускает checks | Worker | `creating_pr`, `failed`, `reviewing`, `cancelled` | test log, check results |
| `creating_pr` | Создается PR | Worker | `reviewing`, `failed` | branch, commit sha, PR URL |
| `reviewing` | Claude/CI/CodeRabbit review | Worker | `needs_fix`, `ready_for_human`, `failed` | review.md, CI status |
| `needs_fix` | Есть blockers | Review runner | `fixing`, `failed`, `cancelled` | blocker list |
| `fixing` | Codex исправляет blockers | Worker | `testing`, `failed`, `cancelled` | fix.log, attempt number |
| `ready_for_human` | Готово к ручному review/merge | Worker | `done`, `failed` | PR URL, summary, checks |
| `done` | Human отметил завершение после merge или решения | Human/Bot | terminal | merge sha or closure note |
| `failed` | Ошибка выполнения | Worker | terminal or manual retry | failure reason, failed step |
| `cancelled` | Задача отменена | Bot/Worker | terminal | cancellation reason |

## Правила переходов

- Нельзя переходить из `created` сразу в `implementing`.
- Нельзя создавать PR без branch и worktree.
- Нельзя ставить `ready_for_human` без PR URL или явного non-coding результата.
- Нельзя ставить `done` автоматически после PR creation.
- `done` не означает auto-merge. В MVP это ручной статус после человеческого решения.
- Fix loop должен иметь лимит попыток.

