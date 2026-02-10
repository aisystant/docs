#!/usr/bin/env python3
"""
Валидатор Markdown по правилам format-guide.md.

Проверяет (12 пунктов чек-листа):
 1. YAML front matter (title, order, type, aisystant_code)
 2. Один H1 после front matter, совпадает с title
 3. Две пустые строки между --- и H1
 4. Типы подразделов (type соответствует заголовку)
 5. Английские имена файлов и папок (нет кириллицы)
 6. Изображения в assets/ с именами fig-XX, файл существует
 7. Сноски (каждая ссылка [^N] имеет определение [^N]:)
 8. index.md в каждой папке-секции
 9. Pandoc-артефакты ({.underline}, {.mark}, ---, --, ** в title)
10. Имена файлов в kebab-case, NN- префикс, без точек
11. Таблицы в pipe-формате (нет grid-таблиц Pandoc: +---+---+)
12. Нет simple-таблиц Pandoc (строки из тире с пробелами)

Использование:
    python3 validate.py <directory>
"""

import argparse
import logging
import os
import re
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Правила определения типа по заголовку (дублирует convert.py)
# ---------------------------------------------------------------------------

def expected_type_for_title(title):
    """Определить ожидаемый type по заголовку (None = не можем определить)."""
    title_lower = title.lower()
    if re.match(r"моделирование\s+\d+\.\d+\.\s*понятия", title_lower):
        return "table"
    if "моделирование" in title_lower:
        return "table"
    if "вопросы для повторения" in title_lower:
        return "checklist"
    if "домашнее задание" in title_lower:
        return "checklist"
    if title_lower.startswith("задания"):
        return "checklist"
    if re.match(r"задач[иа][\s:]", title_lower):
        return "multiple_choice"
    if "выводы раздела" in title_lower or "саммари раздела" in title_lower:
        return "text"
    return "text"


# ---------------------------------------------------------------------------
# Результат валидации
# ---------------------------------------------------------------------------

class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, filepath, line_num, message):
        self.errors.append(f"ERROR [{filepath}:{line_num}] {message}")

    def warn(self, filepath, line_num, message):
        self.warnings.append(f"WARN  [{filepath}:{line_num}] {message}")

    def file_error(self, filepath, message):
        self.errors.append(f"ERROR [{filepath}] {message}")

    def file_warn(self, filepath, message):
        self.warnings.append(f"WARN  [{filepath}] {message}")

    @property
    def ok(self):
        return len(self.errors) == 0

    def summary(self):
        return f"{len(self.errors)} ошибок, {len(self.warnings)} предупреждений"


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def parse_frontmatter(lines):
    """Извлечь front matter как dict и вернуть (fm_dict, end_idx) или (None, None)."""
    if len(lines) < 3 or lines[0].strip() != "---":
        return None, None

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, None

    fm = {}
    for line in lines[1:end_idx]:
        m = re.match(r"^(\w[\w_]*):\s*(.*)", line)
        if m:
            key = m.group(1)
            val = m.group(2).strip().strip('"').strip("'")
            fm[key] = val
    return fm, end_idx


def has_cyrillic(text):
    """Проверить, содержит ли текст кириллицу."""
    return bool(re.search(r"[а-яА-ЯёЁ]", text))


# ---------------------------------------------------------------------------
# Проверки
# ---------------------------------------------------------------------------

def check_frontmatter(filepath, lines, is_index, is_root_index, result):
    """[1] Проверить YAML front matter: title, order, type, aisystant_code."""
    fm, end_idx = parse_frontmatter(lines)

    if fm is None:
        result.error(filepath, 1, "Нет YAML front matter (должен начинаться с ---)")
        return None, None

    if "title" not in fm:
        result.error(filepath, 1, "В front matter нет поля 'title'")
    if "order" not in fm:
        result.error(filepath, 1, "В front matter нет поля 'order'")

    # index.md НЕ должен иметь type
    if is_index and "type" in fm:
        result.warn(filepath, 1, "index.md не должен содержать поле 'type'")

    # Обычные файлы ДОЛЖНЫ иметь type
    if not is_index and "type" not in fm:
        result.error(filepath, 1, "В front matter нет поля 'type' (text/table/checklist/multiple_choice)")

    # Корневой index.md должен иметь aisystant_code
    if is_root_index and "aisystant_code" not in fm:
        result.warn(filepath, 1, "Корневой index.md не содержит поля 'aisystant_code'")

    return fm, end_idx


def check_h1_and_title_match(filepath, lines, fm, fm_end_idx, result):
    """[2][3] Проверить H1 после front matter, совпадение с title, две пустые строки."""
    if fm_end_idx is None:
        return

    remaining = lines[fm_end_idx + 1:]

    # Считать пустые строки до H1
    empty_count = 0
    h1_idx = None
    h1_text = None
    for i, line in enumerate(remaining):
        if line.strip() == "":
            empty_count += 1
        elif line.startswith("# "):
            h1_idx = fm_end_idx + 1 + i
            h1_text = line[2:].strip()
            break
        else:
            result.warn(filepath, fm_end_idx + 2 + i,
                        f"Между --- и H1 неожиданный контент: '{line.strip()[:40]}'")
            break

    if h1_idx is None:
        result.warn(filepath, fm_end_idx + 1, "Нет заголовка H1 после front matter")
        return

    # [3] Две пустые строки
    if empty_count < 2:
        result.warn(filepath, h1_idx + 1,
                    f"После --- должны быть 2 пустые строки перед H1 (найдено {empty_count})")

    # [2] Только один H1
    h1_count = sum(1 for line in lines if re.match(r"^# [^#]", line))
    if h1_count > 1:
        result.warn(filepath, 1, f"Найдено {h1_count} заголовков H1, ожидается 1")

    # [2] Title в YAML совпадает с H1
    if fm and "title" in fm and h1_text:
        if fm["title"] != h1_text:
            result.warn(filepath, h1_idx + 1,
                        f"YAML title '{fm['title'][:50]}' ≠ H1 '{h1_text[:50]}'")


def check_type_matches_title(filepath, fm, result):
    """[4] Проверить что type соответствует заголовку."""
    if fm is None or "type" not in fm or "title" not in fm:
        return

    actual_type = fm["type"]
    expected = expected_type_for_title(fm["title"])

    if expected and actual_type != expected:
        result.warn(filepath, 1,
                    f"type '{actual_type}' не соответствует заголовку "
                    f"(ожидается '{expected}' для '{fm['title'][:40]}')")


def check_english_name(filepath, target_dir, result):
    """[5] Проверить что имена файлов и папок на английском (нет кириллицы)."""
    rel_path = os.path.relpath(filepath, target_dir)
    parts = rel_path.split(os.sep)
    for part in parts:
        name = os.path.splitext(part)[0]
        if has_cyrillic(name):
            result.file_error(filepath,
                              f"Кириллица в имени: '{part}' (должно быть на английском)")


def check_english_dirname(dirpath, target_dir, result):
    """[5] Проверить что имя директории на английском."""
    dirname = os.path.basename(dirpath)
    if has_cyrillic(dirname):
        result.file_error(dirpath,
                          f"Кириллица в имени папки: '{dirname}' (должно быть на английском)")


def check_images(filepath, lines, result):
    """[6] Проверить ссылки на изображения: assets/, fig-XX, файл существует."""
    file_dir = os.path.dirname(filepath)

    for i, line in enumerate(lines, 1):
        img_match = re.search(r"!\[([^\]]*)\]\(([^)]+)\)", line)
        if not img_match:
            continue

        img_path = img_match.group(2)

        # Путь должен начинаться с assets/
        if not img_path.startswith("assets/"):
            result.warn(filepath, i, f"Изображение не в assets/: {img_path}")

        # Формат имени fig-XX
        img_name = os.path.basename(img_path)
        if not re.match(r"fig-\d{2}", img_name):
            result.warn(filepath, i,
                        f"Имя изображения не соответствует fig-XX: {img_name}")

        # Файл существует
        full_img_path = os.path.join(file_dir, img_path)
        if not os.path.exists(full_img_path):
            result.error(filepath, i,
                         f"Изображение не найдено: {img_path}")


def check_footnotes(filepath, lines, result):
    """[7] Проверить что каждая ссылка [^N] имеет определение [^N]:."""
    text = "".join(lines)

    # Найти все ссылки [^N] (не определения)
    refs = set(re.findall(r"\[\^(\d+)\](?!:)", text))
    # Найти все определения [^N]:
    defs = set(re.findall(r"^\[\^(\d+)\]:", text, re.MULTILINE))

    # Ссылки без определений
    orphan_refs = refs - defs
    if orphan_refs:
        result.error(filepath, 1,
                     f"Ссылки без определений: {', '.join(f'[^{r}]' for r in sorted(orphan_refs, key=int))}")

    # Определения без ссылок
    orphan_defs = defs - refs
    if orphan_defs:
        result.warn(filepath, 1,
                    f"Определения без ссылок: {', '.join(f'[^{d}]' for d in sorted(orphan_defs, key=int))}")


def check_pandoc_artifacts(filepath, lines, fm, result):
    """[9] Проверить отсутствие Pandoc-артефактов."""
    for i, line in enumerate(lines, 1):
        # {.underline}, {.mark} и другие span-атрибуты
        if re.search(r"\{\.[\w-]+\}", line):
            result.warn(filepath, i,
                        f"Pandoc span-атрибут: '{re.search(r'{.[^}]+}', line).group()}'")

        # --- или -- вместо — (только в тексте, не YAML-делимитеры, не HR)
        stripped = line.strip()
        if stripped == "---" or stripped == "":
            continue
        if re.search(r" --- | -- ", line):
            result.warn(filepath, i,
                        "Pandoc-тире: ' --- ' или ' -- ' вместо ' — '")

    # ** или * в YAML title
    if fm and "title" in fm:
        title = fm["title"]
        if "**" in title or re.search(r"(?<!\*)\*(?!\*)", title):
            result.warn(filepath, 1,
                        f"Markdown-разметка в YAML title: '{title[:50]}'")

    # Bold-артефакты вокруг точки: word**.** или standalone **\**
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped in ("**\\**", "****"):
            result.warn(filepath, i, "Standalone bold-артефакт: **\\**")
        elif re.search(r"[^*]\*\*\.\*\*", line):
            result.warn(filepath, i,
                        "Bold-артефакт вокруг точки: X**.**")
        elif re.search(r"\*\*\*\*\.\*\*", line):
            result.warn(filepath, i,
                        "Bold-артефакт: ****.**")


def check_grid_tables(filepath, lines, result):
    """[11] Проверить отсутствие grid-таблиц Pandoc (+---+---+)."""
    for i, line in enumerate(lines, 1):
        if re.match(r'^\+[-=+]+\+\s*$', line.strip()):
            result.error(filepath, i,
                         "Grid-таблица Pandoc (нужен pipe-формат). "
                         "Исправить: python3 fix_grid_tables.py <файл>")
            return  # Одной ошибки достаточно для файла


def check_simple_tables(filepath, lines, result):
    """[12] Проверить отсутствие simple-таблиц Pandoc (строки из тире с пробелами)."""
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip YAML delimiters and horizontal rules
        if stripped == '---' or stripped == '':
            continue
        # Simple table separator: groups of dashes separated by spaces, 10+ dashes total
        if re.match(r'^[-\s]+$', stripped) and stripped.count('-') >= 10:
            if re.search(r'-{3,}', stripped):
                result.error(filepath, i,
                             "Simple-таблица Pandoc (нужен pipe-формат). "
                             "Исправить: python3 fix_simple_tables.py <файл>")
                return  # Одной ошибки достаточно для файла


def check_filename(filepath, result):
    """[10] Проверить имя файла: kebab-case, NN- префикс, без точек."""
    basename = os.path.basename(filepath)
    name_part = os.path.splitext(basename)[0]

    if basename == "index.md":
        return

    # Точки в имени
    if "." in name_part:
        result.file_warn(filepath,
                         f"Точка в имени файла: {basename} (используйте тире)")

    # Заглавные буквы
    if re.search(r"[A-Z]", name_part):
        result.file_warn(filepath,
                         f"Заглавные буквы в имени файла: {basename}")

    # NN- префикс
    if not re.match(r"^\d{2}-", name_part):
        result.file_warn(filepath,
                         f"Имя файла без NN- префикса: {basename}")


def check_dirname(dirpath, result):
    """[10] Проверить имя директории: без точек, NN- префикс."""
    dirname = os.path.basename(dirpath)
    if "." in dirname and dirname != ".git":
        result.file_warn(dirpath,
                         f"Точка в имени папки: {dirname} (используйте тире)")


# ---------------------------------------------------------------------------
# Основная функция
# ---------------------------------------------------------------------------

def validate_directory(target_dir):
    """Запустить все 12 проверок на директории."""
    result = ValidationResult()

    if not os.path.isdir(target_dir):
        result.file_error(target_dir, "Директория не существует")
        return result

    md_files = []
    dirs_with_md = set()

    for root, dirs, files in os.walk(target_dir):
        # Пропустить assets и скрытые папки
        dirs[:] = [d for d in dirs if d != "assets" and not d.startswith(".")]

        # [5][10] Проверить имена директорий
        for d in dirs:
            dirpath = os.path.join(root, d)
            check_dirname(dirpath, result)
            check_english_dirname(dirpath, target_dir, result)

        for f in files:
            if not f.endswith(".md"):
                continue
            filepath = os.path.join(root, f)
            md_files.append(filepath)
            dirs_with_md.add(root)

            # Прочитать файл
            with open(filepath, "r", encoding="utf-8") as fh:
                lines = fh.readlines()

            is_index = (f == "index.md")
            is_root_index = (f == "index.md" and root == target_dir)

            # [1] YAML front matter
            fm, fm_end = check_frontmatter(filepath, lines, is_index, is_root_index, result)

            # [2][3] H1 и совпадение с title
            if fm_end:
                check_h1_and_title_match(filepath, lines, fm, fm_end, result)

            # [4] Тип подраздела
            if not is_index:
                check_type_matches_title(filepath, fm, result)

            # [5] Английские имена
            check_english_name(filepath, target_dir, result)

            # [6] Изображения
            check_images(filepath, lines, result)

            # [7] Сноски
            check_footnotes(filepath, lines, result)

            # [9] Pandoc-артефакты
            check_pandoc_artifacts(filepath, lines, fm, result)

            # [10] Имена файлов
            check_filename(filepath, result)

            # [11] Grid-таблицы
            check_grid_tables(filepath, lines, result)

            # [12] Simple-таблицы
            check_simple_tables(filepath, lines, result)

    # [8] index.md в каждой папке с .md файлами
    for dir_path in dirs_with_md:
        index_path = os.path.join(dir_path, "index.md")
        if not os.path.exists(index_path):
            result.file_warn(dir_path, "Нет index.md в директории")

    log.info("Проверено %d .md файлов в %d директориях", len(md_files), len(dirs_with_md))
    return result


def main():
    parser = argparse.ArgumentParser(description="Валидатор Markdown по format-guide.md (12 проверок)")
    parser.add_argument("directory", help="Директория для проверки")
    parser.add_argument("--strict", action="store_true",
                        help="Считать предупреждения ошибками")
    args = parser.parse_args()

    result = validate_directory(args.directory)

    # Вывод результатов
    if result.errors:
        log.info("\n=== ОШИБКИ ===")
        for e in result.errors:
            log.info(e)

    if result.warnings:
        log.info("\n=== ПРЕДУПРЕЖДЕНИЯ ===")
        for w in result.warnings:
            log.info(w)

    log.info("\n=== ИТОГО: %s ===", result.summary())

    if args.strict and result.warnings:
        sys.exit(1)
    if result.errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
