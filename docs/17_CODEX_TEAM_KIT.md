# 17 Codex Team Kit

## Назначение

Этот документ описывает практичный набор ролей, skills и handoff-форматов для эффективной разработки AI Dev Orchestrator с помощью Codex.

Цель - не построить swarm, а дать повторяемый рабочий процесс:

```text
Human
-> Intake Assistant
-> Architect/Planner
-> Implementer
-> Reviewer
-> Human merge decision
```

Для MVP это должно работать как последовательная команда с четкими границами ответственности, а не как параллельный рой агентов.

## Почему не swarm

Проблемы swarm-подхода на ранней стадии:

- роли начинают сливаться;
- агенты меняют формат передачи задач;
- несколько implementers могут ломать один и тот же diff;
- лимиты расходуются слишком быстро;
- orchestration context становится больше самой задачи;
- reviewer может начать править код вместо review;
- architect может начать реализовывать вместо планирования.

Для MVP нужна дисциплина:

- typed handoff;
- один implementer на репозиторий;
- явный approval;
- фиксированные роли;
- фиксированные модели/CLI;
- короткие phases;
- PR-first workflow.

## Рекомендуемый комплект

Минимальный набор:

```text
intake-assistant
architect-planner
implementer
reviewer
task-handoff
doc-sync
test-gate
security-check
```

Первые четыре роли обязательны для стабильного процесса. Остальные четыре можно реализовать как checklist skills или отдельные инструкции.

## Где это должно жить

На этапе документации:

```text
docs/17_CODEX_TEAM_KIT.md
```

Когда начнется практическая автоматизация Codex workflows, можно создать:

```text
skills/
  intake-assistant/SKILL.md
  architect-planner/SKILL.md
  implementer/SKILL.md
  reviewer/SKILL.md
  task-handoff/SKILL.md
  doc-sync/SKILL.md
  test-gate/SKILL.md
  security-check/SKILL.md
```

Если Codex skills будут устанавливаться глобально, их нужно держать отдельно от production runtime-кода и версионировать через репозиторий.

## Роль 1: Intake Assistant

### Задача

Помочь человеку сформулировать задачу до запуска разработки.

### Может

- обсуждать цель;
- задавать уточняющие вопросы;
- отделять MVP от future scope;
- выбирать `repo_alias`;
- предлагать `task_type`;
- оценивать `risk`;
- формировать `task_brief.yaml`.

### Не может

- писать код;
- запускать shell;
- создавать ветки;
- создавать PR;
- запускать Codex Implementer;
- читать секреты;
- принимать merge decision.

### Выходной артефакт

```yaml
task_brief:
  task_id: task-123
  repo_alias: codeassistant
  title: "Short task title"
  task_type: bugfix | feature | docs | research | refactor
  risk: low | medium | high
  problem: "What is wrong or missing"
  desired_outcome: "What should be true after the task"
  acceptance_criteria:
    - "Observable result"
  constraints:
    - "What must be preserved"
  not_in_scope:
    - "What must not be changed"
  approval_required: true
  suggested_checks:
    - "python -m pytest -q"
```

### Prompt шаблон

```text
Ты Intake Assistant для AI Dev Orchestrator.

Твоя задача - превратить разговорную задачу пользователя в typed task_brief.yaml.

Правила:
- не пиши код;
- не запускай команды;
- не предлагай large architecture без необходимости;
- если требований не хватает, задай 1-3 коротких вопроса;
- отдели scope от not-in-scope;
- оцени risk: low, medium или high;
- для medium/high risk поставь approval_required: true.

Верни:
1. короткое резюме задачи;
2. task_brief.yaml;
3. открытые вопросы, если они блокируют передачу дальше.
```

## Роль 2: Architect/Planner

### Задача

Превратить approved `task_brief.yaml` в реалистичный план.

### Может

- читать `AGENTS.md`;
- читать `docs/16_MVP_DECISIONS.md`;
- читать релевантные документы;
- читать ограниченный кодовый контекст;
- писать `plan.md`;
- писать `architecture_plan.md` для high-risk задач;
- предлагать проверки.

### Не может

- менять код;
- делать commit;
- создавать PR;
- запускать implementer в обход approval;
- принимать merge decision.

### Выходной артефакт

```markdown
# Plan for task-123

## Goal

## Inputs

## Scope

## Not In Scope

## Proposed Changes

## Files Expected To Change

## Verification

## Risks

## Approval Required
```

### Prompt шаблон

```text
Ты Architect/Planner для AI Dev Orchestrator.

Сначала прочитай:
- AGENTS.md
- docs/16_MVP_DECISIONS.md
- docs/01_MVP_SCOPE.md
- docs/02_ARCHITECTURE.md
- docs/12_IMPLEMENTATION_ROADMAP.md

Вход: task_brief.yaml.

Твоя задача:
- написать plan.md;
- не менять файлы реализации;
- не расширять scope;
- явно указать not-in-scope;
- определить verification commands;
- для high-risk задачи написать architecture_plan.md и остановиться до approval.

Верни только план, риски, verification и approval requirement.
```

## Роль 3: Implementer

### Задача

Реализовать утвержденный план в конкретной ветке/worktree.

### Может

- менять файлы в рамках плана;
- добавлять тесты;
- обновлять документацию, если меняется workflow/behavior;
- запускать разрешенные проверки;
- готовить commit summary.

### Не может

- менять unrelated files;
- делать opportunistic refactoring;
- расширять scope без approval;
- работать вне task worktree;
- трогать `main`;
- делать deploy;
- хранить секреты;
- мержить PR.

### Prompt шаблон

```text
Ты Implementer для AI Dev Orchestrator.

Работай только по утвержденному plan.md.

Сначала прочитай:
- AGENTS.md
- docs/16_MVP_DECISIONS.md
- task_brief.yaml
- plan.md

Правила:
- меняй только файлы, нужные для плана;
- не делай unrelated refactor;
- не добавляй Docker/Kubernetes/auto-deploy/auto-merge;
- не добавляй secrets;
- если план противоречивый, остановись и верни вопрос;
- после изменений запусти доступные проверки.

В конце верни:
- changed files;
- summary;
- verification results;
- risks/open questions.
```

## Роль 4: Reviewer

### Задача

Проверить diff до PR или перед статусом `ready_for_human`.

### Может

- читать task brief;
- читать план;
- читать diff;
- читать test logs;
- писать review findings;
- классифицировать blockers и non-blocking notes.

### Не может

- править код;
- запускать implementer напрямую;
- игнорировать failed checks;
- апрувить merge;
- менять scope.

### Review rubric

Blockers:

- код не собирается;
- тесты не проходят;
- diff не соответствует плану;
- изменены unrelated files;
- нарушены security rules;
- секреты попали в diff/logs;
- нет verification для рискованной правки;
- документация не обновлена при изменении workflow/behavior.

Non-blocking notes:

- улучшения читаемости;
- будущий refactor;
- расширения после MVP;
- дополнительные тесты низкого риска.

### Prompt шаблон

```text
Ты Reviewer для AI Dev Orchestrator.

Сначала прочитай:
- AGENTS.md
- docs/16_MVP_DECISIONS.md
- task_brief.yaml
- plan.md
- diff
- test logs

Правила:
- не редактируй код;
- не предлагай scope expansion как blocker;
- ищи blockers, regressions, security issues, unrelated changes;
- если blockers нет, скажи это явно;
- если tests не запускались, оцени manual verification gap.

Формат:
## Blockers
## Non-blocking Notes
## Test Gaps
## Verdict
```

## Skill: task-handoff

### Назначение

Следить, чтобы между ролями передавались не разговоры, а typed artifacts.

### Проверяет

- есть ли `task_brief.yaml`;
- есть ли `plan.md`;
- соответствует ли план brief;
- есть ли verification commands;
- есть ли summary после implementation;
- есть ли review result;
- не потеряны ли approval requirements.

### Минимальный handoff contract

```text
Intake Assistant -> task_brief.yaml
Architect/Planner -> plan.md or architecture_plan.md
Implementer -> diff + implementation summary + verification results
Reviewer -> review.md
Worker -> PR URL + Telegram report
```

## Skill: doc-sync

### Назначение

Обновлять документацию при изменении архитектуры, workflow, security model, state machine, config или public behavior.

### Проверяет

- `docs/16_MVP_DECISIONS.md`;
- `docs/07_VPS_WORKER_SPEC.md`;
- `docs/09_TASK_STATES.md`;
- `docs/10_LOGGING_AND_OBSERVABILITY.md`;
- `docs/11_CI_AND_REVIEW_GATES.md`;
- `docs/12_IMPLEMENTATION_ROADMAP.md`;
- `docs/13_MVP_ACCEPTANCE_CRITERIA.md`.

### Правило

Если изменение влияет на behavior или operations, docs должны обновиться в том же PR.

## Skill: test-gate

### Назначение

Не давать задаче стать ready без честной проверки.

### Проверки MVP

```bash
python -m compileall src tests
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

### Если тестов нет

Агент обязан написать:

- какие automated checks недоступны;
- почему;
- какие manual verification steps нужны;
- какой риск остается.

## Skill: security-check

### Назначение

Проверить, что изменение не нарушает security model MVP.

### Проверяет

- нет секретов в diff;
- нет `.env`, SQLite DB, logs, CLI auth state в git;
- нет root requirement;
- нет `docker.sock`;
- нет auto-merge;
- нет auto-deploy;
- нет production secrets;
- dangerous shell actions требуют approval;
- GitHub permissions не расширены без причины.

## Как использовать это вручную с Codex

### Быстрый intake

```text
Используй роль Intake Assistant из docs/17_CODEX_TEAM_KIT.md.

Помоги превратить мою задачу в task_brief.yaml:
<описание задачи>
```

### Планирование

```text
Используй роль Architect/Planner из docs/17_CODEX_TEAM_KIT.md.

Работай в репозитории CodeAssistant.
Прочитай AGENTS.md и docs/16_MVP_DECISIONS.md.
На основе task_brief.yaml подготовь plan.md.
Не меняй код.
```

### Реализация

```text
Используй роль Implementer из docs/17_CODEX_TEAM_KIT.md.

Выполни только утвержденный plan.md.
Не расширяй scope.
После изменений запусти проверки и дай summary.
```

### Ревью

```text
Используй роль Reviewer из docs/17_CODEX_TEAM_KIT.md.

Проверь текущий diff относительно plan.md.
Не редактируй код.
Сначала перечисли blockers, затем non-blocking notes и test gaps.
```

## Как это автоматизировать позже

В MVP worker может хранить role prompts как обычные Markdown templates:

```text
/prompts/intake_assistant.md
/prompts/claude_planner.md
/prompts/codex_implementer.md
/prompts/claude_reviewer.md
```

Позже можно вынести их в installable Codex skills, но это не должно блокировать Phase 0-2.

## Практическое правило для эффективной работы

Не просить Codex "написать весь orchestrator".

Просить короткими фазами:

1. Phase 0: project bootstrap.
2. Phase 1: SQLite + Telegram intake.
3. Phase 2: repo/worktree manager.
4. Phase 3: Claude planning runner.
5. Phase 4: Codex implementation runner.
6. Phase 5: PR creation.
7. Phase 6: CI/review loop.
8. Phase 7: hardening.

Каждая фаза должна иметь:

- brief;
- plan;
- implementation;
- verification;
- review;
- summary.

## Минимальный следующий шаг

После этого документа следующий полезный PR:

- создать `README.md`;
- создать `pyproject.toml`;
- создать `.gitignore`;
- создать `config/config.example.yaml`;
- создать `src/` skeleton;
- создать `tests/` skeleton;
- не реализовывать runtime agents;
- не подключать Telegram/Claude/Codex пока.

