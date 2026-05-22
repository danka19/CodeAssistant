# 11 CI And Review Gates

## CI для MVP

CI может быть минимальным. Главное - PR не должен считаться готовым без отчета о проверках.

Минимальные варианты:

- Python: `ruff`, `pytest`.
- Node: `npm test`, `npm run lint`, `npm run build`.
- C++/Qt: configure/build command, unit tests если есть.
- Docs-only: markdown lint опционально, manual verification допустим.

Если в проекте нет тестов, агент должен явно написать manual verification steps и пометить это в PR.

## Review gates

Обязательные gates:

- Claude review.
- CI status или явная фиксация отсутствия CI.
- Human review.
- Manual merge.

Optional gates:

- CodeRabbit PR review.
- GPT independent critic для high risk.
- Дополнительный local smoke test.

## Ready criteria

PR может получить статус `ready_for_human`, если:

- PR создан;
- diff соответствует плану;
- unrelated files не изменены;
- build/test/lint выполнены или честно описана их недоступность;
- Claude review не нашел blockers;
- blockers исправлены или явно оставлены на human decision;
- documentation/manual verification обновлены при необходимости.

## Serious blockers

Серьезные blockers:

- код не собирается;
- тесты не проходят;
- изменение unrelated files;
- нарушение публичных API без approval;
- отсутствие проверки для рискованного изменения;
- нарушение архитектуры;
- потеря документации;
- потенциальное удаление данных;
- небезопасные команды;
- секреты попали в diff, prompt или log;
- PR меняет protected branch settings;
- реализация не соответствует утвержденному плану.

## Fix loop

MVP должен ограничивать fix loop, например двумя попытками. Если blockers остаются, задача переходит в `needs_fix` или `failed` с понятной причиной и ссылками на логи.

## Manual merge

Даже если CI и AI review успешны, merge выполняет человек. Agent может только подготовить PR и статус `ready_for_human`.

