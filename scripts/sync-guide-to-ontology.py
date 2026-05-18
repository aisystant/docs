#!/usr/bin/env python3
"""
sync-guide-to-ontology.py

Синхронизация guide-файлов с PACK-personal/ontology.md §2.

Функции:
- Читает ontology.md §2, строит словарь терминов
- Сканирует guide-файлы, парсит frontmatter (introduces / uses)
- Проверяет дрейф: понятия в guide, отсутствующие в ontology
- Обновляет pack_refs в frontmatter (опция --write)
- Проверяет якорные ссылки (опция --check-links)

Режимы:
  --dry-run     Только отчёт, ничего не пишет
  --check       CI-mode: exit(1) при дрейфе или битых ссылках
  --write       Обновляет файлы (default без флагов = --dry-run)

Использование:
  python3 scripts/sync-guide-to-ontology.py --write
  python3 scripts/sync-guide-to-ontology.py --check
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import frontmatter

IWE_ROOT = Path(__file__).resolve().parents[2]  # scripts/ → docs/ → IWE/
DEFAULT_ONTOLOGY = IWE_ROOT / "PACK-personal" / "ontology.md"
DEFAULT_GUIDES_DIR = IWE_ROOT / "docs" / "docs" / "ru" / "personal-design"
ONTOLOGY_RELATIVE_FROM_GUIDES = "../../../PACK-personal/ontology.md"


def slugify(text: str) -> str:
    """Преобразует термин в якорь: lowercase, пробелы/ё → дефисы."""
    text = text.lower().replace("ё", "е")
    return re.sub(r"[^a-z0-9а-я]+", "-", text).strip("-")


def parse_ontology_table(path: Path) -> Dict[str, Dict]:
    """
    Парсит таблицу §2 Глоссарий домена из ontology.md.
    Возвращает: {термин: {definition, parent, source, status, anchor}}
    """
    content = path.read_text(encoding="utf-8")
    # Найти начало таблицы §2
    match = re.search(r"## 2\.\s*Глоссарий домена.*?(\n\|[^\n]+\|\n\|[^\n]+\|)", content, re.S)
    if not match:
        # fallback: ищем первую таблицу после "## 2."
        match = re.search(r"## 2\..*?(\n\| Термин \| Определение \|)", content, re.S)
    if not match:
        raise RuntimeError("Не найдена таблица §2 в ontology.md")

    # Найти все строки таблицы
    # Таблица markdown: | **Термин** | Определение | ... |
    table_start = match.start(1)
    table_text = content[table_start:]
    # Конец таблицы — пустая строка или новый заголовок
    table_end_match = re.search(r"\n\n(?=#{1,6}\s)", table_text)
    if table_end_match:
        table_text = table_text[: table_end_match.start()]

    terms: Dict[str, Dict] = {}
    for line in table_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        # Убрать пустые крайние ячейки (markdown table edge)
        cells = cells[1:-1]
        if len(cells) < 4:
            continue
        term_raw = cells[0]
        # Пропустить заголовок
        if "Термин" in term_raw and "Определение" in cells[1]:
            continue
        if "-" * 5 in term_raw:
            continue
        # Извлечь термин без markdown bold
        term = re.sub(r"\*\*([^*]+)\*\*", r"\1", term_raw).strip()
        if not term:
            continue
        definition = cells[1]
        parent = cells[2] if len(cells) > 2 else ""
        source = cells[3] if len(cells) > 3 else ""
        status = cells[4] if len(cells) > 4 else ""
        anchor = slugify(term)
        terms[term] = {
            "definition": definition,
            "parent": parent,
            "source": source,
            "status": status,
            "anchor": anchor,
        }
    return terms


def _parse_yaml_list(val) -> List[str]:
    """Парсит YAML-список или строку в список строк."""
    if isinstance(val, list):
        return [str(v).strip() for v in val if v]
    elif isinstance(val, str):
        return [val.strip()]
    return []


def extract_frontmatter_concepts(text: str) -> Set[str]:
    """
    Извлекает понятия из frontmatter без полного YAML-парсинга.
    Работает даже с невалидным YAML (двоеточия в строках без кавычек).
    """
    concepts: Set[str] = set()
    # Найти блок между первыми ---
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.S | re.M)
    if not m:
        return concepts
    fm = m.group(1)

    # introduces
    intro = re.search(r"^introduces:\s*(.+)$", fm, re.M)
    if intro:
        raw = intro.group(1).strip()
        if raw.startswith("[") and raw.endswith("]"):
            items = [x.strip().strip('"').strip("'") for x in raw[1:-1].split(",")]
            concepts.update(i for i in items if i)
        else:
            concepts.add(raw)

    # uses
    uses = re.search(r"^uses:\s*(.+)$", fm, re.M)
    if uses:
        raw = uses.group(1).strip()
        if raw.startswith("[") and raw.endswith("]"):
            items = [x.strip().strip('"').strip("'") for x in raw[1:-1].split(",")]
            concepts.update(i for i in items if i)
        elif raw:
            # Многострочный список с -
            if re.search(r"^\s*- ", raw, re.M):
                items = re.findall(r"^\s*- (.+)$", raw, re.M)
                concepts.update(i.strip() for i in items if i.strip())
            else:
                concepts.add(raw)

    # pack_refs
    pack_match = re.search(r"^pack_refs:\s*\n((?:\s+- .+\n?)+)", fm, re.M)
    if pack_match:
        block = pack_match.group(1)
        for line in block.splitlines():
            concept_m = re.search(r"concept:\s*(.+)", line)
            if concept_m:
                concepts.add(concept_m.group(1).strip().strip('"').strip("'"))

    return concepts


def get_concepts_from_frontmatter(post) -> Set[str]:
    """Извлекает понятия из frontmatter keys: introduces, uses, pack_refs[].concept"""
    concepts: Set[str] = set()
    for key in ("introduces", "uses"):
        val = post.get(key)
        concepts.update(_parse_yaml_list(val))
    # Также из pack_refs
    pack_refs = post.get("pack_refs", [])
    if isinstance(pack_refs, list):
        for ref in pack_refs:
            if isinstance(ref, dict) and "concept" in ref:
                concepts.add(ref["concept"].strip())
    return concepts


def make_pack_refs(concepts: Set[str], ontology: Dict[str, Dict]) -> List[Dict]:
    """Генерирует pack_refs для понятий, найденных в ontology."""
    refs = []
    for concept in sorted(concepts, key=lambda x: x.lower()):
        info = ontology.get(concept)
        if not info:
            continue
        refs.append(
            {
                "concept": concept,
                "source": info.get("source", ""),
                "ontology_anchor": f"{ONTOLOGY_RELATIVE_FROM_GUIDES}#{info['anchor']}",
            }
        )
    return refs


def update_frontmatter_pack_refs(
    post, ontology: Dict[str, Dict]
) -> Tuple[frontmatter.Post, bool]:
    """
    Обновляет pack_refs в frontmatter на основе introduces + uses.
    Возвращает (updated_post, changed).
    """
    concepts = get_concepts_from_frontmatter(post)
    new_refs = make_pack_refs(concepts, ontology)
    existing_refs = post.get("pack_refs", [])
    if not isinstance(existing_refs, list):
        existing_refs = []
    # Сравнить как множества
    existing_set = {
        (r.get("concept"), r.get("ontology_anchor"))
        for r in existing_refs
        if isinstance(r, dict)
    }
    new_set = {(r["concept"], r["ontology_anchor"]) for r in new_refs}
    if existing_set == new_set:
        return post, False
    post.metadata["pack_refs"] = new_refs
    return post, True


def scan_guides(guides_dir: Path) -> List[Path]:
    """Возвращает список .md файлов в директории guide."""
    return sorted(guides_dir.rglob("*.md"))


def check_links(file_path: Path, ontology: Dict[str, Dict]) -> List[str]:
    """Проверяет якорные ссылки в markdown-файле."""
    content = file_path.read_text(encoding="utf-8")
    issues = []
    # Найти все ссылки вида [text](../../../PACK-personal/ontology.md#anchor)
    pattern = re.compile(
        r"\[([^\]]+)\]\(" + re.escape(ONTOLOGY_RELATIVE_FROM_GUIDES) + r"#([^)]+)\""
    )
    for match in pattern.finditer(content):
        anchor = match.group(2)
        # Проверить, есть ли такой anchor в ontology
        found = any(info["anchor"] == anchor for info in ontology.values())
        if not found:
            issues.append(f"  Битая ссылка: anchor '#{anchor}' не найден в ontology")
    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Синхронизация guide-файлов с PACK-personal/ontology.md"
    )
    parser.add_argument(
        "--ontology", type=Path, default=DEFAULT_ONTOLOGY, help="Путь к ontology.md"
    )
    parser.add_argument(
        "--guides-dir", type=Path, default=DEFAULT_GUIDES_DIR, help="Директория с guide-файлами"
    )
    parser.add_argument("--dry-run", action="store_true", help="Только отчёт, не писать файлы")
    parser.add_argument("--check", action="store_true", help="CI-mode: exit(1) при проблемах")
    parser.add_argument("--write", action="store_true", help="Обновить файлы")
    parser.add_argument("--check-links", action="store_true", help="Проверить якорные ссылки")
    args = parser.parse_args()

    if not args.ontology.exists():
        print(f"ERROR: ontology не найден: {args.ontology}", file=sys.stderr)
        sys.exit(1)

    ontology = parse_ontology_table(args.ontology)
    print(f"Загружено {len(ontology)} терминов из ontology.md §2")

    guides = scan_guides(args.guides_dir)
    print(f"Найдено {len(guides)} guide-файлов")

    all_guide_concepts: Set[str] = set()
    drift: List[Tuple[Path, str]] = []  # (файл, понятие)
    changed_files: List[Path] = []
    link_issues: List[Tuple[Path, List[str]]] = []

    dry_run = not args.write and (args.dry_run or not args.write)
    # Если --write явно указан — пишем. Если ничего не указано — dry-run.
    if args.write:
        dry_run = False

    for guide_path in guides:
        raw_text = guide_path.read_text(encoding="utf-8")
        fallback_concepts = extract_frontmatter_concepts(raw_text)
        try:
            post = frontmatter.load(str(guide_path))
            concepts = get_concepts_from_frontmatter(post)
        except Exception as e:
            # Fallback для невалидного YAML
            concepts = fallback_concepts
            post = None

        all_guide_concepts.update(concepts)

        for c in concepts:
            if c not in ontology:
                drift.append((guide_path, c))

        # Обновить pack_refs только если frontmatter распарсился
        if post is not None:
            updated_post, changed = update_frontmatter_pack_refs(post, ontology)
            if changed:
                if dry_run:
                    print(f"[DRY-RUN] Будет обновлён: {guide_path}")
                else:
                    frontmatter.dump(updated_post, str(guide_path), sort_keys=False)
                    changed_files.append(guide_path)

        # Проверить ссылки
        if args.check_links:
            issues = check_links(guide_path, ontology)
            if issues:
                link_issues.append((guide_path, issues))

    # Отчёт
    print("\n" + "=" * 60)
    print("ОТЧЁТ СИНХРОНИЗАЦИИ")
    print("=" * 60)

    if drift:
        print(f"\n⚠️  ДРЕЙФ: {len(drift)} понятий из guide отсутствуют в ontology:")
        by_file: Dict[Path, List[str]] = {}
        for path, concept in drift:
            by_file.setdefault(path, []).append(concept)
        for path, concepts in sorted(by_file.items(), key=lambda x: str(x[0])):
            print(f"  {path}:")
            for c in sorted(set(concepts)):
                print(f"    - {c}")
    else:
        print("\n✅ Дрейфа нет: все понятия из guide найдены в ontology")

    if changed_files:
        print(f"\n📝 Обновлено файлов: {len(changed_files)}")
        for p in changed_files:
            print(f"  {p}")
    else:
        print("\n📝 Изменений pack_refs не требуется")

    if link_issues:
        print(f"\n🔗 Битых ссылок: {sum(len(i) for _, i in link_issues)}")
        for path, issues in link_issues:
            print(f"  {path}:")
            for issue in issues:
                print(issue)
    elif args.check_links:
        print("\n🔗 Битых ссылок не найдено")

    # Резюме
    total_guide_concepts = len(all_guide_concepts)
    covered = sum(1 for c in all_guide_concepts if c in ontology)
    coverage = (covered / total_guide_concepts * 100) if total_guide_concepts else 100
    print(f"\n📊 Покрытие ontology: {covered}/{total_guide_concepts} ({coverage:.1f}%)")

    if args.check:
        has_issues = bool(drift) or bool(link_issues)
        if has_issues:
            print("\n❌ CHECK FAILED — обнаружены проблемы", file=sys.stderr)
            sys.exit(1)
        else:
            print("\n✅ CHECK PASSED")
            sys.exit(0)


if __name__ == "__main__":
    main()
