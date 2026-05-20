# Спецификация проверок контента в конвейере (Content Validation Spec)

> Статус: аудит текущего состояния. После утверждения — переход в `process/` как обязательная спецификация.

## 1. Архитектура конвейера

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Локальная      │     │  Pull Request   │     │  CI / CD        │
│  разработка     │────▶│  (review)       │────▶│  (GitHub Actions)│
│                 │     │                 │     │                 │
│ • pre-commit    │     │ • PR template   │     │ • build         │
│ • lint scripts  │     │ • code review   │     │ • deploy        │
│ • unit tests    │     │ • auto-checks   │     │ • release       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────┐                          ┌─────────────────┐
│  Cross-repo     │                          │  Post-deploy    │
│  drift detection│                          │  smoke tests    │
│                 │                          │                 │
│ • curriculum    │                          │ • link check    │
│   notification  │                          │ • health check  │
│ • ontology sync │                          │                 │
└─────────────────┘                          └─────────────────┘
```

## 2. Точки валидации (Gates)

### Gate 0 — Локальная разработка (pre-commit / pre-push)

| Проверка | Репо | Инструмент | Статус | Владелец |
|----------|------|------------|--------|----------|
| **R4 — ID коллизии** | PACK-* | `check-pack-collisions.sh` | ✅ Есть (pre-commit hook) | CI + локально |
| **Auto-MAP** | PACK-* | `generate-map.py` | ✅ Есть (pre-commit hook) | Авто |
| **Markdown lint (12 rules)** | docs | `scripts/convert_word/validate.py` | ⚠️ Есть, но НЕ в CI | Локально |
| **FPF drift (ontology vs guide)** | docs | `scripts/sync-guide-to-ontology.py` | ❌ Нет | — |
| **Битые ссылки (cross-repo)** | docs | grep на `../../../PACK-*` | ❌ Нет | — |
| **Frontmatter completeness** | docs | скрипт проверки полей | ❌ Нет | — |

**Проблема:** В docs-репо нет pre-commit hooks вообще. Все проверки (validate.py, sync-guide-to-ontology.py) запускаются вручную. Человек может закоммитить сломанный frontmatter, битые ссылки и drift — и узнает об этом только при ручном аудите.

### Gate 1 — Pull Request (ручной + автоматический review)

| Проверка | Репо | Инструмент | Статус | Владелец |
|----------|------|------------|--------|----------|
| **PR template (Universal Bans, Hard Gates, Change-Type checks)** | PACK-* | `.github/pull_request_template.md` | ✅ Есть | Автор PR |
| **PR template для руководств** | docs | — | ❌ Нет | — |
| **Автоматическая проверка drift** | docs | `sync-guide-to-ontology.py --check` | ❌ Нет | — |
| **Автоматическая проверка битых ссылок** | docs | grep / lychee | ❌ Нет | — |
| **Review checklist для v4.1 формата** | docs | — | ❌ Нет | — |

**Проблема:** В docs-репо нет PR template. Автор PR не проходит через чеклист content validation. Ревьюер проверяет "на глаз".

### Gate 2 — CI (GitHub Actions)

#### PACK-personal

| Workflow | Что проверяет | Статус |
|----------|---------------|--------|
| `pack-lint.yml` | R4 ID collision detection | ✅ Работает |
| `notify-curriculum.yml` | Уведомление DS-principles-curriculum при изменении PD.FORM.089 | ✅ Работает |

#### docs (aisystant/docs)

| Workflow | Что проверяет | Статус |
|----------|---------------|--------|
| `build-and-deploy.yaml` | Docker build → Nomad deploy | ✅ Работает (только build) |
| `build-releases.yaml` | pandoc → epub → GitHub Release | ✅ Работает |
| `vkcloud-s3-static-deploy.yaml` | VitePress build → static deploy | ✅ Работает |
| `translate.yaml` | Diff переводов | ⚠️ Ручной запуск |
| `patch-caddy-iwe-routes.yaml` | Caddy config | ⚠️ Ручной запуск |

**Чего нет в CI docs:**
- ❌ `validate.py` — markdown lint (12 rules)
- ❌ `sync-guide-to-ontology.py --check` — drift detection
- ❌ Проверка битых ссылок
- ❌ Проверка frontmatter (format_version, pack_refs, etc.)
- ❌ FPF compliance check
- ❌ Проверка word count (target vs actual)
- ❌ Проверка completeness (все обязательные секции подраздела присутствуют)

### Gate 3 — Post-deploy (smoke tests)

| Проверка | Статус |
|----------|--------|
| **Сайт открывается** | ✅ Неявно (deploy завершается успешно) |
| **Ссылки работают** | ❌ Нет |
| **epub собирается без ошибок** | ✅ Частично (build-releases.yaml) |
| **Онтология доступна на сайте** | ❌ Нет (ontology.md не деплоится) |

### Gate 4 — Cross-repo drift detection

| Проверка | Репо | Инструмент | Статус |
|----------|------|------------|--------|
| **Pack → Curriculum notification** | PACK-personal | `notify-curriculum.yml` | ✅ Работает |
| **Ontology → Guide sync** | docs | `sync-guide-to-ontology.py` | ⚠️ Только ручной |
| **Guide → Ontology back-sync** | docs | — | ❌ Нет |

## 3. Gap Analysis (чего не хватает)

### Критичные (блокеры качества)

| # | Проблема | Последствие | Где внедрять |
|---|----------|-------------|--------------|
| G1 | `sync-guide-to-ontology.py --check` не в CI | Drift между онтологией и руководствами накапливается | CI docs + pre-commit |
| G2 | `validate.py` не в CI | Markdown с артефактами, broken frontmatter, grid-таблицы попадают в main | CI docs |
| G3 | Нет проверки битых ссылок | Все `../../../PACK-personal/ontology.md#*` ссылки битые на GitHub | CI docs + pre-commit |
| G4 | Нет PR template для docs | Автор PR не проходит content validation checklist | PR template |
| G5 | Нет pre-commit hooks в docs | Локальные ошибки (drift, ссылки) попадают в коммит | pre-commit hook |

### Важные (деградация качества)

| # | Проблема | Последствие | Где внедрять |
|---|----------|-------------|--------------|
| G6 | Нет проверки FPF compliance | Определения отклоняются от канона (как с U.Method) | PR checklist + ручной audit |
| G7 | Нет проверки completeness подраздела | Пропущены обязательные блоки (степени мастерства, проверка себя) | CI docs |
| G8 | Нет проверки word count | Целевой объём 500–1500 слов не контролируется | CI docs (warning) |
| G9 | Нет post-deploy link check | Битые ссылки остаются на production | Post-deploy smoke test |

## 4. Рекомендуемая схема внедрения

### Этап 1 — Немедленно (блокеры)

```yaml
# .github/workflows/content-validation.yaml (docs)
name: Content Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install deps
        run: pip install pyyaml
      - name: Markdown lint (12 rules)
        run: python scripts/convert_word/validate.py docs/ru/personal-design/
      - name: Ontology drift check
        run: python scripts/sync-guide-to-ontology.py --check
      - name: Broken link detection
        run: |
          ! grep -r "../../../PACK-personal/ontology.md#" docs/docs/ru/personal-design/
      - name: Frontmatter completeness
        run: |
          # Проверка, что format_version и pack_refs присутствуют
          python scripts/check-frontmatter.py docs/docs/ru/personal-design/
```

```bash
# pre-commit hook (docs/.git/hooks/pre-commit)
#!/bin/bash
set -e
python3 scripts/sync-guide-to-ontology.py --check || true
! grep -r "../../../PACK-personal/ontology.md#" docs/docs/ru/personal-design/ || {
  echo "❌ Обнаружены битые cross-repo ссылки"
  exit 1
}
```

```markdown
# .github/pull_request_template.md (docs)
## Content Validation Checklist
- [ ] Все новые понятия есть в ontology.md (или добавлены туда)
- [ ] Нет битых ссылок на PACK-personal
- [ ] FPF compliance: определения не противоречат канону (или помечены как педагогическая интерпретация)
- [ ] Обязательные блоки подраздела присутствуют (понятия, мем, из Pack, объяснение, минимальный шаг, степени мастерства, проверка себя)
- [ ] Frontmatter заполнен (format_version, pack_refs, introduces, uses)
```

### Этап 2 — Важное

- Добавить `lychee` или `markdown-link-check` в CI для проверки всех внутренних ссылок
- Добавить post-deploy smoke test: curl на ключевые страницы + проверка 200
- Добавить word count check (warning, не error)

### Этап 3 — Оптимизация

- Автоматический FPF compliance checker (на основе ontology.md §2 + FPF-Spec.md)
- Автоматическая генерация "missing concepts" отчёта при drift

## 5. Текущий инвентарь инструментов

| Инструмент | Локация | Назначение | Где используется |
|------------|---------|------------|------------------|
| `check-pack-collisions.sh` | PACK-personal/.github/scripts/ | R4 ID collision detection | CI PACK + pre-commit |
| `pack-lint.sh` | DS-MCP/knowledge-mcp/scripts/ | Pack lint (WP-242) | pre-commit PACK |
| `generate-map.py` | SPF/scripts/ | Auto-regenerate MAP | pre-commit PACK |
| `validate.py` | docs/scripts/convert_word/ | Markdown lint (12 rules) | Локально (ручной) |
| `sync-guide-to-ontology.py` | docs/scripts/ | Drift detection + frontmatter sync | Локально (ручной) |
| `build.py` | docs/scripts/build_releases/ | Release assembly | CI (build-releases.yaml) |
| `iwe_event_emit.sh` | .claude/lib/ | Cross-repo event emission | post-commit hook |

---

*Аудит проведён: 2026-05-18. Следующий шаг — утверждение спецификации и создание workflow/content-validation.yaml + PR template + pre-commit hook.*
