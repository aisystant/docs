---
id: PD.PROCESS.001
title: "Процесс обнаружения дрейфа руководств от Pack (Drift Detection)"
status: active
created: 2026-05-23
updated: 2026-05-23
wp: 300
---

# Процесс обнаружения дрейфа руководств от Pack

> **Цель:** Автоматически выявлять расхождения между текстами универсальных руководств (Guide 1–4) и исходными формами Pack PD (Source of Truth), чтобы предотвратить устаревание материалов.

---

## 1. Триггеры проверки

| Триггер | Что запускает | Кто ответственный | SLA |
|---------|--------------|-------------------|-----|
| **Изменение Pack** | Commit в `PACK-personal/ontology.md` или `PACK-personal/*.md` с `PD.FORM.*` / `PD.METHOD.*` | GitHub Actions (`pack-drift-watcher.yml`) | ≤ 2 мин (issue) |
| **Регулярная проверка** | Расписание: еженедельно, понедельник 05:00 EEST | GitHub Actions (`v4-lint.yml` schedule) | — |
| **Ручной запрос** | Пилот или автор руководства вызывает `v4-lint.py pack-drift` | Автор руководства или Портной | ≤ 24 ч |
| **Week Close** | Ритуал закрытия недели (`/week-close`) | Оркестратор / Навигатор | В рамках Week Close |

---

## 2. Автоматическая проверка (CI)

### 2.1 Pack-drift-watcher (при изменении Pack)

**Workflow:** `pack-drift-watcher.yml`
**Репозиторий:** `PACK-personal`
**Действие:**
1. При push в `main` → сравнивает `ontology.md` §2 с `introduces` во всех Guide-файлах.
2. Если найдены отсутствующие `ontology_anchor` или новые FORM/METHOD без отражения в руководствах → создаёт issue в `docs` репозитории с тегом `pack-drift`.
3. Issue содержит: список затронутых понятий, ссылки на FORM/METHOD, рекомендуемые разделы для проверки.

### 2.2 Регулярный lint (еженедельный)

**Workflow:** `v4-lint.yml`
**Расписание:** `cron: '0 5 * * 1'` (Пн 05:00 EEST)
**Действие:**
1. Запускает `v4-lint.py pack-drift` на всех 4 руководствах.
2. Результат: PR comment или issue при `errors > 0`.
3. При `warnings > 0` → summary в PR comment, не блокирует merge.

### 2.3 Pre-commit hook (локально)

**Скрипт:** `pre-commit-docs.sh`
**Действие:** При коммите в `docs/ru/personal-design/*` проверяет `pack_refs` и `introduces` на consistency с `ontology.md`.
**Если FAIL** → коммит блокируется с инструкцией по исправлению.

---

## 3. Ручной процесс (Week Close)

**Шаг 1.** Портной (R27) или Навигатор (R26) запускает:
```bash
cd docs
python3 ../DS-principles-curriculum/tools/v4-lint.py pack-drift \
  docs/ru/personal-design/ \
  --ontology ../PACK-personal/ontology.md
```

**Шаг 2.** Если выявлен drift:
- Записать в `drift-log/YYYY-MM-DD.md` (создать если нет).
- Пометить affected подразделы тегом `pack-drift-pending` в frontmatter.
- Создать задачу в WeekPlan следующей недели (WP-new или обновление существующего).

**Шаг 3.** Автор руководства (или Kimi/Claude по назначению):
- Проверяет affected подразделы.
- Обновляет текст или `pack_refs`.
- Перезапускает `v4-lint.py subsection` на изменённых файлах.
- Коммитит с тегом `[pack-drift]`.

---

## 4. Ответственные

| Роль | Обязанность |
|------|-------------|
| **Портной (R27)** | Еженедельный drift-check в рамках Week Close. Постановка задач на синхронизацию. |
| **Автор руководства** | Исправление affected подразделов в течение недели после обнаружения. |
| **CI (GitHub Actions)** | Автоматическое обнаружение и создание issue. |
| **Пилот** | Решение конфликтных случаев (escalation), когда drift требует архитектурного решения. |

---

## 5. Критерии приёмки (Definition of Done drift-fix)

- [ ] `v4-lint.py pack-drift` проходит без errors на affected подразделах.
- [ ] `v4-lint.py subsection` проходит без errors на изменённых файлах.
- [ ] Изменения закоммичены с тегом `[pack-drift]`.
- [ ] `ontology.md` обновлён, если изменения затронули определения понятий.
- [ ] Проверена кросс-руководная consistency (`v4-lint.py cross-guide`).

---

## 6. Исключения (когда drift — допустим)

1. **Умышленное упрощение:** руководство использует педагогическую интерпретацию понятия (например, «Метод = способ действия» вместо FPF-канона). Зафиксировано в `ontology.md` как `pedagogical_alias`.
2. **Out-of-scope понятия:** понятие из Pack не входит в границы руководства (bounded context). Зафиксировано в структурном файле руководства.
3. **Legacy-формализация:** понятие из старой версии Pack, помеченное как deprecated. Не требует синхронизации.

---

*Зафиксировано при закрытии WP-300. Peer-reviewed by Claude (DP.SC.154).*
