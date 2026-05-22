# 14 Risks And Limitations

## Риски

| Риск | Вероятность | Влияние | Mitigation | Что делать в MVP |
|---|---:|---:|---|---|
| Подписки Claude/ChatGPT не всегда подходят для автоматизации как сервиса | Medium | High | Проверить условия использования и CLI auth model | Проектировать runner заменяемым, не завязывать систему на один способ auth |
| API billing может понадобиться позже | Medium | Medium | Отделить runner interface от billing/auth | В MVP фиксировать usage вручную или простыми логами без сложной cost analytics |
| Лимиты могут закончиться | High | Medium | Timeouts, retries, понятный failed state | При лимите ставить `failed` с причиной и возможностью manual retry |
| Агенты могут сделать неверный diff | High | High | Plan, diff review, CI, Claude review, human merge | Не считать PR готовым без review gates |
| Агент может переусложнить решение | Medium | Medium | Scope control, no opportunistic refactoring | В AGENTS.md запретить unrelated refactor |
| CI может отсутствовать | Medium | Medium | Manual verification required | Явно писать отсутствие CI и steps |
| C++/Qt проекты могут требовать специфичной локальной среды | Medium | High | Repo-specific setup docs, prepared VPS image | Для MVP начать с одного тестового репозитория с понятной средой |
| GUI-проверки сложно автоматизировать на VPS | High | Medium | Headless tests, manual verification, screenshots only later | Не включать GUI automation в MVP |
| Секреты и tokens требуют осторожности | High | High | Redaction, scoped tokens, env secrets | Запретить secrets в prompts/logs/code |
| Telegram может быть недостаточным UI для сложного дебага | Medium | Medium | Store full logs on disk, short Telegram status | В MVP Telegram только для команд/status, debug через VPS/GitHub |
| Worker может зависнуть на subprocess | Medium | Medium | Timeouts, process groups, cancellation | Ввести timeout на agent/test commands |
| Worktree может остаться грязным после сбоя | Medium | Medium | Per-task worktree, status checks, cleanup policy | Не переиспользовать worktree между задачами |
| Review loop может стать бесконечным | Medium | Medium | Limit attempts | Ограничить fix attempts |
| GitHub token может быть слишком широким | Medium | High | Scoped token или GitHub App | Минимальные permissions, protected main |
| Неверная классификация риска | Medium | Medium | Human approval for ambiguous tasks | Если сомнение, считать medium/high |

## Ограничения MVP

- Один VPS.
- Один worker process.
- Один или несколько заранее настроенных repo aliases.
- Telegram как простой command interface.
- SQLite вместо внешней БД.
- Нет web dashboard.
- Нет auto-deploy.
- Нет auto-merge.
- Нет production secrets.
- Нет payments.
- Нет browser automation.

## Принцип реакции на риск

Если действие может повредить код, данные, безопасность или деньги, MVP должен остановиться и запросить approval. Если approval flow еще не реализован для этого действия, задача должна завершиться с понятным `failed` или `waiting_approval`.

