# 01 MVP Scope

## Цель MVP

Собрать минимальную систему, которую можно поднять на арендованном Linux VPS и использовать для полного цикла: Telegram task -> planning -> implementation -> checks -> Pull Request -> Telegram report.

MVP не должен быть универсальной агентной платформой. Он должен быть маленьким, понятным и проверяемым.

## MVP должен уметь

- Принимать задачу из Telegram через `/task`.
- Создавать уникальный `task_id`.
- Сохранять задачу, статус и метаданные в SQLite.
- Определять минимальный тип задачи: small, medium, large/risky, documentation, research.
- Создавать feature branch вида `agent/task-123-short-slug`.
- Создавать отдельный git worktree под задачу.
- Запускать Claude planning step.
- Сохранять план в `/runs/task-123/plan.md`.
- Для medium/high risk задач переводить задачу в `waiting_plan_approval`.
- Запускать Codex implementation step после плана или approval.
- Сохранять stdout/stderr и structured events.
- Запускать build/test/lint commands, если они настроены для репозитория.
- Фиксировать отсутствие тестов и manual verification steps.
- Делать commit в feature branch.
- Push feature branch.
- Создавать PR через `gh pr create` или GitHub API.
- Отправлять Telegram-отчет со статусом, summary, проверками и ссылкой на PR.
- Не мержить автоматически.

## Минимальные сущности MVP

- `Task`: исходная задача, статус, риск, репозиторий, ветка, worktree, PR URL.
- `Run`: попытка выполнения задачи.
- `Event`: лог изменения состояния.
- `Approval`: решение пользователя по плану или опасному действию.
- `CheckResult`: результат build/test/lint/CI/review.

## MVP не обязан уметь

- Сложный web UI.
- Voice input.
- Life assistant.
- Покупки и платежи.
- Browser automation.
- Auto-deploy.
- Auto-merge.
- Kubernetes.
- Temporal или другой workflow engine.
- Multi-agent swarm.
- Сложная аналитика стоимости.
- Поддержка многих пользователей.
- Полноценный RBAC.
- Управление production secrets.

## Границы MVP

MVP может быть однопроцессным приложением с SQLite и файловыми логами. Допустимо использовать systemd service или Docker Compose. Главный критерий - надежный end-to-end путь для одной задачи в одном репозитории.

Если в проекте нет тестов или CI, MVP не должен притворяться, что проверка пройдена. Он обязан явно писать: automated checks unavailable, manual verification required.

