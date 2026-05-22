# 00 Project Overview

## Что строим

AI Dev Orchestrator - простую агентную систему разработки для Linux VPS. Система принимает задачи из Telegram, создает отдельную ветку и git worktree, запускает Claude для анализа и планирования, запускает Codex для реализации, выполняет проверки, создает Pull Request в GitHub и присылает отчет обратно в Telegram.

Финальное слияние в `main` всегда остается ручным.

## Зачем строим

Цель - получить практичный workflow для разработки небольших и средних задач без ручного переключения между Telegram, GitHub, CLI-агентами, worktree, тестами и PR. Система должна экономить время на glue-work, но не заменять человеческое архитектурное решение и финальный merge.

## Какие проблемы решаем

- Потеря контекста между постановкой задачи и реализацией.
- Ручное создание веток, worktree, логов и PR.
- Непрозрачность работы CLI-агентов.
- Отсутствие единого состояния задачи.
- Слабая воспроизводимость агентных запусков.
- Риск случайных изменений в `main`.
- Необходимость получать статус и ссылку на PR в удобном канале.

## Что входит в MVP

- Telegram intake для новых задач.
- SQLite task database.
- Генерация `task_id`.
- Создание branch и git worktree.
- Claude planning step.
- Сохранение `plan.md`.
- Optional approval для medium/high risk задач.
- Codex implementation step.
- Сохранение логов.
- Запуск build/test/lint, если команды настроены.
- Создание PR через GitHub CLI или GitHub API.
- Telegram-отчет со статусом и ссылкой на PR.
- CI и review gates.
- Ручной merge.

## Что не входит в MVP

- Большой web UI.
- Kubernetes, Temporal или сложный orchestrator.
- Devin-like платформа.
- Multi-agent swarm.
- Voice input.
- Browser automation.
- Auto-deploy.
- Auto-merge.
- Life assistant.
- Платежи и покупки.
- Сложная аналитика стоимости.

## Почему GitHub-first

GitHub уже является устойчивым source of truth для кода, веток, PR, CI, review и protected branch rules. MVP должен использовать эти готовые механизмы, а не дублировать их в собственной системе.

GitHub-first подход дает:

- понятную историю изменений;
- стандартные PR и review;
- CI как обязательный gate;
- ручной контроль merge;
- совместимость с CodeRabbit и другими PR-review инструментами;
- возможность восстановить состояние даже при сбое VPS worker.

## Почему не начинаем с большого оркестратора

Первый MVP должен доказать workflow, а не построить инфраструктурную платформу. Для одного владельца и нескольких репозиториев достаточно маленького Python worker, SQLite, git worktree, GitHub CLI и systemd или Docker Compose.

Большой orchestrator добавит сложность раньше, чем появятся реальные требования к масштабированию: очереди, retries, UI, распределенные воркеры, tenancy, quotas и сложная observability.

## Почему dev-agent system и life-assistant лучше разделять

Dev-agent system работает с кодом, репозиториями, токенами GitHub, CI и локальными командами. Life-assistant может работать с календарем, покупками, личными данными, платежами и браузером. Это разные security domains.

В MVP их нужно разделять:

- разные секреты;
- разные permissions;
- разные approval gates;
- разные логи;
- разные риски;
- отсутствие доступа dev-agent к платежам, production secrets и личным интеграциям.

