# 13 MVP Acceptance Criteria

MVP считается готовым, когда выполнены все критерии ниже.

## End-to-end criteria

- Я могу отправить `/task` в Telegram.
- Система создает задачу в базе.
- Система присваивает `task_id`.
- Система создает branch.
- Система создает git worktree.
- Claude создает `plan.md`.
- Для крупной задачи есть approval перед реализацией.
- Codex делает изменение в тестовом репозитории.
- Система запускает configured checks или явно пишет, что автоматических проверок нет.
- Система создает PR.
- Telegram присылает ссылку на PR.
- Main защищен от прямого merge.
- Логи доступны в `/runs/task-123`.
- При ошибке задача получает `failed` и понятную причину.
- Merge остается ручным.

## Documentation criteria

- Есть `AGENTS.md`.
- Описан Telegram bot.
- Описан VPS worker.
- Описан GitHub PR flow.
- Описаны роли Claude/Codex/CodeRabbit/Human.
- Описаны security gates.
- Описаны task states.
- Описаны logs.
- Описаны CI/review gates.
- Описаны риски и ограничения.

## Security criteria

- Worker работает не под root.
- Agent token не может push в `main`.
- Secrets не попадают в git.
- Secrets не попадают в logs.
- Dangerous commands требуют approval или блокируются.
- Production deploy и payments отсутствуют в MVP.

## Failure criteria

MVP должен корректно обрабатывать:

- GitHub auth failure;
- Claude failure;
- Codex failure;
- test failure;
- PR creation failure;
- cancellation;
- missing CI;
- no tests configured.

Корректная обработка означает: статус задачи обновлен, причина записана, пользователь получил Telegram notification.

