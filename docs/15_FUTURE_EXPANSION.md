# 15 Future Expansion

Этот документ описывает расширения после MVP. Эти пункты не должны попадать в scope первого MVP.

## Возможные улучшения

- Web UI.
- Task dashboard.
- Cline Kanban.
- OpenHands smoke test.
- Voice input.
- Periodic tasks.
- Monitoring.
- Life-assistant отдельным контуром.
- Local models for classification.
- Multi-agent mode.
- Alternative implementation branches.
- GPT as independent critic.
- Support for multiple repositories.
- Support for multiple users.
- Integration with Jira/Linear.
- Deployment gates.

## Web UI

Может заменить часть Telegram debug flow: список задач, статусы, ссылки на логи, approvals, фильтры. Не нужен для MVP, потому что Telegram + GitHub достаточно для первого end-to-end workflow.

## Task dashboard

Полезен после появления десятков задач. До этого SQLite и Telegram `/status` проще.

## Cline Kanban

Можно использовать для визуального управления задачами, если появится устойчивый поток задач и потребность в board view.

## OpenHands smoke test

Может стать дополнительным validation layer, но не должен быть обязательным dependency MVP.

## Voice input

Удобно для постановки задач, но добавляет speech-to-text, ошибки распознавания и security concerns. После MVP.

## Periodic tasks and monitoring

Можно добавить scheduled checks: проверка CI, stale PR, dependency alerts. Это отдельный режим, не базовый task execution loop.

## Life-assistant

Должен быть отдельным контуром:

- отдельные secrets;
- отдельные approvals;
- отдельные logs;
- отсутствие доступа к dev repo tokens без необходимости;
- отдельная модель риска.

## Local models for classification

Можно использовать дешевые локальные модели для первичной классификации задач, но в MVP достаточно простых правил и Claude planning.

## Multi-agent mode

Параллельные агенты, competition branches или swarm mode стоит добавлять только после стабильного single-agent workflow.

## Alternative implementation branches

Для сложных задач можно генерировать два варианта решения в разных ветках и сравнивать. Это повышает качество, но увеличивает стоимость и сложность.

## GPT as independent critic

Можно подключать GPT для независимой критики high-risk решений, особенно при архитектуре, C++/Qt многопоточности, SDK integration и больших refactoring.

## Multiple repositories and users

После MVP можно добавить:

- repo registry;
- per-repo commands;
- permissions per user;
- audit by user;
- quotas.

## Jira/Linear integration

Может стать источником задач или местом синхронизации статусов. Не нужен до стабильного Telegram/GitHub loop.

## Deployment gates

Deploy должен оставаться отдельным этапом после MVP. Для него нужны отдельные approvals, secrets, environments, rollback plan и audit.

