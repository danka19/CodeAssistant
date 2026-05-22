# 08 GitHub Flow

## Основные правила

- `main` protected.
- Прямой push в `main` запрещен.
- Все изменения идут через feature branches.
- Branch pattern: `agent/task-123-short-slug`.
- Каждый результат оформляется Pull Request.
- CI checks обязательны.
- Merge всегда ручной.
- CodeRabbit optional.

## Branch naming

Формат:

```text
agent/task-123-short-slug
```

Требования:

- `task-123` соответствует task id в SQLite.
- `short-slug` строится из задачи и не должен содержать секреты.
- High risk задачи можно помечать label `risk-high`, а не особым branch name.

## Labels

Рекомендуемые labels:

- `agent-task`
- `agent-planning`
- `agent-implementing`
- `agent-review`
- `agent-needs-fix`
- `agent-ready-for-human`
- `agent-failed`
- `risk-low`
- `risk-medium`
- `risk-high`

## PR lifecycle

1. Worker создает PR после commit/push.
2. PR получает labels `agent-task` и risk label.
3. CI запускается автоматически.
4. Claude review создает `review.md` и может оставить PR comment.
5. CodeRabbit review работает как optional слой.
6. Если есть blockers, PR получает `agent-needs-fix`.
7. После fix и успешных проверок PR получает `agent-ready-for-human`.
8. Human принимает решение и мержит вручную.

## PR template

```markdown
## Goal

What this task is trying to change.

## Plan

Link or summary from runs/task-123/plan.md.

## Changed Files

- file paths and short explanations

## Tests

- automated checks run
- CI status

## Documentation

- docs/changelog updates
- not needed because ...

## Risks

- known risks
- rollback notes if relevant

## Manual Verification

- steps when automated tests are missing or insufficient

## AI Review Summary

- Claude review result
- CodeRabbit result if enabled
- blockers fixed or remaining notes
```

## Protected main settings

Минимум:

- Require pull request before merging.
- Require status checks to pass.
- Require conversation resolution.
- Disallow force pushes.
- Disallow deletions.
- Restrict direct pushes for agent token.

## Что не делать в MVP

- Auto-merge.
- Release automation.
- Deploy from PR.
- Branch protection changes by worker.
- Complex merge queue.

