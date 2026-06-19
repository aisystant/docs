---
title: "Staging-среда для руководств v4 (WP-322 Ф2)"
---

# Staging-среда для руководств v4

Эта папка — **staging-витрина** для новых/изменённых подразделов руководств v4, ещё не утверждённых пилотом.

## Жизненный цикл подраздела

```
автор пишет SS → push в staging-v4 → build PASS → пилот проверяет на staging-URL
  → pilot-approved → merge staging-v4 → main → production
```

## Правила

1. **Источник:** ветка `staging-v4` в `aisystant/docs`. Default branch для personal-new-staging.
2. **Структура:** зеркалит `docs/ru/personal-new/` (та же иерархия гайдов/разделов/подразделов).
3. **Build:** при push в `staging-v4` запускается `.github/workflows/staging-build.yaml` — собирает VitePress (без deploy).
4. **Gate merge → main:**
   - PR `staging-v4 → main` обязателен.
   - Label `pilot-approved` обязателен для merge (правило в `.github/CODEOWNERS` + branch protection).
   - Без label — PR не мержится.

## Что сюда кладётся

- **Новые подразделы v4** (после прохождения `/verify subsection` 🔴 + 🟡).
- **Hotfix контент-правки** требующие пилотного ревью.
- **Пилотные эксперименты** с тональностью/практикой (опционально, по запросу автора).

## Что сюда НЕ кладётся

- **Production-готовый контент** — пишется сразу в `docs/ru/personal-new/` на main.
- **Hotfix typo** — мержится в main через `[hotfix]` без staging-gate.

## Связь с другими РП

- **WP-322 Ф2** — это staging (sprint 2 CD-PIPELINE).
- **WP-322 Ф1** — Pack-watcher (sprint 1, уже работает).
- **WP-322 Ф5** — pilot-feedback issue-template (sprint 5, использует staging-URL).
- **WP-300** — содержание подразделов, авторы пишут сюда после `/verify subsection` PASS.

## Текущий статус

⚠️ **Архитектурный фундамент:** ветка `staging-v4` + папка `personal-new-staging/` + build-workflow без deploy.

**Что нужно для полного включения** (отдельная задача для пилота):
- Nomad job `docs-staging` (аналог production job для отдельного URL `staging.docs.aisystant.app`)
- DNS/Caddy для staging-домена
- GitHub branch protection: `staging-v4 → main` требует `pilot-approved` label
- Secret для staging deploy (если отличается от production)

После этого `staging-build.yaml` можно расширить deploy-step'ом.
