# 04 Security Model

## Базовая модель

MVP работает на Linux VPS под отдельным непривилегированным пользователем, например `ai-orchestrator`. Агентная система не должна иметь root-доступ по умолчанию и не должна иметь доступ к production secrets, платежам, покупкам или опасным системным действиям.

## Обязательные ограничения

- Отдельный Linux user для агента.
- Запрет root по умолчанию.
- Запрет `docker.sock` в MVP.
- Scoped GitHub token или GitHub App.
- Protected `main`.
- Required PR review.
- Required status checks.
- Запрет auto-merge.
- Секреты не хранить в prompts, logs, PR body и code.
- Telegram bot token хранить в env/secrets.
- OpenAI/Anthropic auth не логировать.
- Dangerous shell commands должны быть заблокированы или требовать approval.
- Платежи, покупки и production deploy не входят в MVP.

## Секреты

Разрешенные места хранения:

- systemd environment file с правами `600`;
- Docker Compose secrets или `.env` вне git;
- secret manager после MVP.

Запрещено:

- commit секретов;
- запись токенов в `/runs`;
- вывод `env` целиком;
- вставка auth headers в prompts;
- передача production credentials агентам.

## GitHub security

- `main` protected.
- Direct push в `main` запрещен.
- Merge только вручную.
- Required checks должны соответствовать реальному CI проекта.
- Agent token должен иметь минимально нужные permissions:
  - read/write contents для feature branches;
  - pull requests write;
  - checks/status read;
  - issues write опционально.
- Административные настройки репозитория не должны меняться worker без отдельного approval.

## Dangerous commands

MVP должен блокировать или требовать approval для команд, которые:

- удаляют файлы рекурсивно;
- меняют системные директории;
- запускают `sudo`;
- меняют firewall/users/ssh;
- обращаются к `docker.sock`;
- делают deploy;
- очищают git history;
- force-push без разрешения;
- читают произвольные secret files.

## Approval gates

Обязательные approval gates:

- План крупной или рискованной задачи.
- Создание PR, если задача помечена high risk.
- Повторный запуск после blocker-review, если fix может изменить архитектуру.
- Merge.
- Deploy.
- Доступ к новым секретам.
- Подключение сторонних сервисов.
- Изменение security settings.
- Force push.

## MVP policy

В MVP лучше отказать в действии, чем дать агенту широкий доступ. Если задача требует root, production secrets, платежей, auto-deploy или внешних сервисов, worker должен перевести задачу в `failed` или `waiting_approval` с понятным объяснением.

