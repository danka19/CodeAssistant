# 06 Telegram Bot Spec

## Назначение

Telegram bot - основной пользовательский интерфейс MVP. Он принимает задачи, показывает статус, отдает короткие логи и принимает approvals.

Для MVP допустим один разрешенный Telegram user id.

## Команды

### `/task`

- Назначение: создать новую задачу.
- Формат: `/task <repo_alias> <описание задачи>`.
- Пример: `/task greenflow Исправить падение при закрытии окна камеры`.
- Что делает: создает `task_id`, сохраняет input, ставит статус `created`.
- Статус: `created` -> `queued`.
- Ошибки: неизвестный repo alias, пустое описание, пользователь не разрешен, база недоступна.
- Ответ: `Task task-123 accepted. Status: queued.`

### `/status`

- Назначение: показать состояние задачи.
- Формат: `/status <task_id>`.
- Пример: `/status task-123`.
- Что делает: читает SQLite и возвращает статус, branch, PR URL, последний event.
- Статус: не меняет.
- Ошибки: task not found, user not allowed.
- Ответ: `task-123: implementing. Branch: agent/task-123-fix-camera-close.`

### `/log`

- Назначение: показать последние строки task logs.
- Формат: `/log <task_id>`.
- Пример: `/log task-123`.
- Что делает: возвращает tail из `events.jsonl` и ключевых логов.
- Статус: не меняет.
- Ошибки: task not found, logs not available, log too large.
- Ответ: короткий фрагмент без секретов.

### `/approve`

- Назначение: подтвердить план или gated action.
- Формат: `/approve <task_id>`.
- Пример: `/approve task-123`.
- Что делает: записывает approval event.
- Статус: `waiting_plan_approval` -> `implementing` или `queued`.
- Ошибки: task not found, task not waiting approval, user not allowed.
- Ответ: `task-123 approved. Implementation will start.`

### `/reject`

- Назначение: отклонить план.
- Формат: `/reject <task_id> [причина]`.
- Пример: `/reject task-123 слишком большой scope`.
- Что делает: записывает rejection.
- Статус: `waiting_plan_approval` -> `plan_rejected`.
- Ошибки: task not found, task not waiting approval.
- Ответ: `task-123 rejected. Reason saved.`

### `/cancel`

- Назначение: отменить задачу.
- Формат: `/cancel <task_id>`.
- Пример: `/cancel task-123`.
- Что делает: ставит cancel flag, worker останавливает дальнейшие этапы при ближайшей безопасной точке.
- Статус: текущий статус -> `cancelled`, если остановка возможна.
- Ошибки: task not found, already finished, cancellation unsafe at current step.
- Ответ: `task-123 cancellation requested.`

### `/help`

- Назначение: показать команды.
- Формат: `/help`.
- Что делает: отправляет краткую справку.
- Статус: не меняет.
- Ошибки: нет.
- Ответ: список команд и примеры.

## Уведомления

MVP должен отправлять уведомления:

- `task accepted`: задача создана.
- `planning started`: Claude planning запущен.
- `plan ready`: план сохранен.
- `approval required`: нужен `/approve` или `/reject`.
- `implementation started`: Codex запущен.
- `tests started`: build/test/lint начались.
- `PR created`: PR создан, ссылка приложена.
- `review blockers found`: найдены blockers, задача ушла в fix loop или `needs_fix`.
- `task ready`: задача готова к human review.
- `task failed`: задача упала, причина приложена.

## Ограничения сообщений

- Не отправлять большие логи целиком.
- Не отправлять секреты.
- Для длинных summary отправлять путь к файлу или короткую выдержку.
- Inline buttons можно добавить после MVP, но текстовые команды достаточно для первого запуска.

