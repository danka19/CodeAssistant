# 16 MVP Decisions

Дата фиксации: 2026-05-22.

Этот документ фиксирует выбранные решения для первого MVP. Если ранние документы описывают несколько вариантов, решения ниже считаются актуальными для Phase 0-1.

## 1. Режим запуска

Выбран вариант A: `systemd`.

Причины:

- меньше слоев для первого VPS-запуска;
- проще работать с `git`, `gh`, SSH, worktree и файловыми логами;
- проще авторизовать Claude/Codex CLI под отдельным Linux user;
- проще отлаживать через `journalctl` и `/runs`.

Docker Compose не входит в первый MVP. К нему можно вернуться на Phase 7, если понадобится воспроизводимая среда или дополнительная изоляция. `docker.sock` не выдавать агентам в MVP.

## 2. Repo aliases

Для MVP используем два alias.

```yaml
repositories:
  codeassistant:
    repo: danka19/CodeAssistant
    default_branch: main
    purpose: orchestrator_self_development
    local_path: /srv/ai-orchestrator/repos/codeassistant
    worktree_root: /srv/ai-orchestrator/worktrees/codeassistant
    test_commands:
      - python -m compileall src tests
      - python -m pytest -q
      - python -m ruff check .
      - python -m ruff format --check .

  sandbox-py:
    repo: danka19/ai-orchestrator-sandbox
    default_branch: main
    purpose: safe_end_to_end_test_repository
    local_path: /srv/ai-orchestrator/repos/sandbox-py
    worktree_root: /srv/ai-orchestrator/worktrees/sandbox-py
    test_commands:
      - python -m compileall src tests
      - python -m pytest -q
      - python -m ruff check .
      - python -m ruff format --check .
```

`codeassistant` нужен для разработки самого оркестратора. `sandbox-py` нужен как безопасный тестовый репозиторий для первых end-to-end прогонов.

## 3. CI/test команды

Для первого Python-репозитория используем рекомендованный набор:

```bash
python -m compileall src tests
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

Минимальные тестовые зоны для самого оркестратора:

- SQLite schema и migrations;
- task state transitions;
- branch slug generation;
- command allowlist/blocklist;
- secret redaction;
- fake Claude/Codex runners;
- fake GitHub client;
- temporary git repo integration test для worktree.

Если папки `tests` еще нет, команда `compileall` должна быть адаптирована в Phase 0 implementation. Документационная цель остается прежней: automated checks должны быть явными, а их отсутствие не должно маскироваться.

## 4. GitHub auth

Выбран вариант A: fine-grained Personal Access Token.

Минимальные permissions:

- selected repositories only;
- `Contents: read/write`;
- `Pull requests: read/write`;
- `Issues: read/write` опционально для будущей разбивки задач;
- `Metadata: read`.

Не выдавать для MVP:

- `Administration`;
- `Secrets`;
- `Environments`;
- `Deployments`;
- `Workflows`, если нет отдельной необходимости.

GitHub App остается future option. `github_client.py` должен быть спроектирован так, чтобы позже заменить PAT auth на GitHub App без переписывания всего workflow.

## 5. Claude/Codex CLI auth

Выбран вариант A: интерактивная авторизация CLI под Linux user `ai-orchestrator`.

Правила:

- Claude CLI и Codex CLI авторизуются вручную по SSH один раз под тем же user, под которым работает worker;
- worker не должен логировать auth state, token files, env или CLI config;
- API-key режим не включать, пока он не нужен для надежности, лимитов или прозрачной стоимости;
- стоимость и лимиты фиксировать как открытый operational question;
- если login-based режим станет нестабильным или непрозрачным по стоимости, вернуться к API-key варианту с явным budget control.

## 6. Ролевая цепочка MVP

Выбран последовательный pipeline из четырех ролей:

```text
Telegram user
-> Intake Assistant
-> approved Task Brief
-> Claude Planner
-> Codex Implementer
-> Claude Reviewer
-> PR ready for Human
```

Это не multi-agent swarm. В MVP роли запускаются последовательно, с жесткими границами ответственности и typed handoff между этапами.

## 7. Intake Assistant

Intake Assistant сидит перед dev-orchestrator и помогает сформулировать задачу до запуска разработки.

Ответственность:

- обсудить задачу с пользователем;
- уточнить цель, ограничения и ожидаемый результат;
- определить repo alias;
- предложить task type и risk level;
- сформировать `task_brief.yaml`;
- запросить подтверждение brief перед передачей в dev pipeline, если задача не очевидно small;
- не запускать git, shell, Claude Planner, Codex или PR creation напрямую.

Запрещено:

- менять файлы;
- иметь write access к git;
- иметь доступ к production secrets;
- запускать shell-команды;
- создавать PR;
- принимать merge decision.

Минимальные состояния intake:

```text
drafting
waiting_brief_approval
submitted_to_orchestrator
cancelled
```

## 8. Typed handoff

Intake Assistant передает дальше только типизированный brief.

```yaml
task_brief:
  task_id: task-123
  repo_alias: codeassistant
  title: "Short human-readable title"
  task_type: bugfix | feature | docs | research | refactor
  risk: low | medium | high
  problem: "What is wrong or missing"
  desired_outcome: "What should be true after the task"
  acceptance_criteria:
    - "Observable criterion"
  constraints:
    - "What must be preserved"
  not_in_scope:
    - "What must not be changed"
  approval_required: true
  suggested_checks:
    - "python -m pytest -q"
```

`task_brief.yaml` сохраняется в `/runs/task-123/input.md` или `/runs/task-123/task_brief.yaml` и становится главным входом для Claude Planner.

## 9. Claude Planner

Claude Planner получает `task_brief.yaml`, документы проекта и ограниченный repository context.

Ответственность:

- создать `plan.md` для small/medium задач;
- создать `architecture_plan.md` для high-risk задач;
- явно указать scope и not-in-scope;
- предложить проверочные команды;
- отметить, нужен ли approval;
- не менять файлы и не запускать реализацию.

## 10. Codex Implementer

Codex Implementer получает утвержденный `plan.md` и работает только в task worktree.

Ответственность:

- реализовать план;
- добавлять или обновлять тесты;
- не менять unrelated files;
- не расширять scope без остановки и нового approval;
- подготовить diff, commit summary и verification notes.

Ограничение MVP: одновременно не более одного Codex Implementer на один репозиторий.

## 11. Claude Reviewer

Claude Reviewer получает task brief, plan, diff, logs и test results.

Ответственность:

- проверить соответствие реализации плану;
- найти blockers;
- отделить blockers от non-blocking notes;
- написать `review.md`;
- не редактировать код самостоятельно.

Fix loop ограничен одной-двумя попытками. Если blockers остаются, задача переходит в `needs_fix` или `failed` с понятной причиной.

## 12. Модели, лимиты и параллельность

MVP должен фиксировать роль, модель и лимиты в config, а не позволять агентам выбирать это самостоятельно.

Минимальная политика:

- `intake_assistant`: недорогая/быстрая модель или локальная логика, без tools write access;
- `claude_planner`: Claude, planning/review context;
- `codex_implementer`: Codex CLI, write access только в worktree;
- `claude_reviewer`: Claude, read-only review context;
- max concurrent implementers per repo: `1`;
- max fix attempts: `2`;
- max planner pass: `1` для small/medium, отдельный approval для high risk.

Цель ограничений - не сжигать лимиты и не создавать конфликтующие параллельные diff.

