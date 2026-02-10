#!/usr/bin/env python3
"""
Исправление артефактов bold-разметки после конвертации Pandoc.

Паттерны:
1. **\** (standalone) → удалить строку
2. ****.**  → .**  (слияние двойного bold вокруг точки)
3. **word**[^N]**.** → **word[^N].**  (сноска внутри bold)
4. [^N]**.** → [^N].  (убрать bold с точки после сноски)
5. N. word**.** → N. **word.**  (bold label в нумерованном списке)
6. word**.** → word.  (убрать bold с точки в прочих контекстах)

Использование:
    python3 fix_bold_artifacts.py <directory> [--dry-run]
"""

import argparse
import os
import re
import sys


def fix_bold_artifacts(text):
    """Исправить артефакты bold-разметки в тексте."""

    # 1. ****.**  → .**  (слияние: **word****.**  → **word.**)
    text = re.sub(r"\*\*\*\*\.\*\*", ".**", text)

    # 2. **word**[^N]**.** → **word[^N].**
    #    Сноска разрывает bold, а точка отдельно обёрнута в bold
    text = re.sub(
        r"\*\*([^*]+)\*\*(\[\^\d+\])\*\*\.\*\*",
        r"**\1\2.**",
        text,
    )

    # 3. [^N]**.** → [^N].  (оставшиеся сноски перед bold-точкой)
    text = re.sub(r"(\[\^\d+\])\*\*\.\*\*", r"\1.", text)

    # 4. Нумерованные списки: N. word**.** → N. **word.**
    text = re.sub(
        r"^(\d+\.\s+)([а-яА-ЯёЁa-zA-Z]\w*)\*\*\.\*\*",
        r"\1**\2.**",
        text,
        flags=re.MULTILINE,
    )

    # 5. Оставшиеся X**.** → X.  (X = любой символ кроме *)
    text = re.sub(r"([^*])\*\*\.\*\*", r"\1.", text)

    # 6. Standalone **\** или **** → удалить строку
    text = re.sub(r"^\*\*\\?\*\*\s*\n", "", text, flags=re.MULTILINE)

    return text


def process_file(filepath, dry_run=False):
    """Обработать один файл. Возвращает True если были изменения."""
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    fixed = fix_bold_artifacts(original)

    if fixed == original:
        return False

    if dry_run:
        return True

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(fixed)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Исправить артефакты bold-разметки Pandoc"
    )
    parser.add_argument("directory", help="Директория для обработки")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать файлы, не изменяя их",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Директория не найдена: {args.directory}", file=sys.stderr)
        sys.exit(1)

    changed = 0
    total = 0

    for root, dirs, files in os.walk(args.directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if not f.endswith(".md"):
                continue
            filepath = os.path.join(root, f)
            total += 1
            if process_file(filepath, dry_run=args.dry_run):
                changed += 1
                prefix = "[DRY-RUN] " if args.dry_run else ""
                print(f"{prefix}Исправлено: {filepath}")

    action = "Найдено для исправления" if args.dry_run else "Исправлено"
    print(f"\n{action}: {changed} из {total} файлов")


if __name__ == "__main__":
    main()
