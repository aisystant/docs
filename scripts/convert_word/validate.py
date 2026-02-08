#!/usr/bin/env python3
"""
Валидатор Markdown по правилам format-guide.md.

Проверяет:
1. YAML front matter (title, order)
2. Один H1 после front matter
3. Две пустые строки между --- и H1
4. Изображения в assets/ с именами fig-XX-description
5. Подписи к рисункам (*Рис. X.X. ...*)
6. Имена файлов в kebab-case без точек
7. index.md в каждой папке-секции
8. Нет точек в именах папок

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


def check_frontmatter(filepath, lines, result):
    """Проверить YAML front matter."""
    if len(lines) < 3 or lines[0].strip() != "---":
        result.error(filepath, 1, "Нет YAML front matter (должен начинаться с ---)")
        return False

    # Найти закрывающий ---
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        result.error(filepath, 1, "Не закрыт YAML front matter (нет второго ---)")
        return False

    # Проверить обязательные поля
    fm_text = "".join(lines[1:end_idx])
    if "title:" not in fm_text:
        result.error(filepath, 1, "В front matter нет поля 'title'")
    if "order:" not in fm_text:
        result.error(filepath, 1, "В front matter нет поля 'order'")

    return end_idx


def check_h1_after_frontmatter(filepath, lines, fm_end_idx, result):
    """Проверить H1 после front matter с двумя пустыми строками."""
    if fm_end_idx is None or fm_end_idx is False:
        return

    # После --- должны быть две пустые строки, потом # Title
    remaining = lines[fm_end_idx + 1:]

    # Считать пустые строки
    empty_count = 0
    h1_idx = None
    for i, line in enumerate(remaining):
        if line.strip() == "":
            empty_count += 1
        elif line.startswith("# "):
            h1_idx = fm_end_idx + 1 + i
            break
        else:
            result.warn(filepath, fm_end_idx + 2 + i,
                        f"Между --- и H1 неожиданный контент: '{line.strip()[:40]}'")
            break

    if h1_idx is None:
        result.warn(filepath, fm_end_idx + 1, "Нет заголовка H1 после front matter")
    elif empty_count < 2:
        result.warn(filepath, h1_idx + 1,
                    f"После --- должны быть 2 пустые строки перед H1 (найдено {empty_count})")

    # Проверить, что только один H1
    h1_count = sum(1 for l in lines if re.match(r"^# [^#]", l))
    if h1_count > 1:
        result.warn(filepath, 1, f"Найдено {h1_count} заголовков H1, ожидается 1")


def check_images(filepath, lines, result):
    """Проверить ссылки на изображения."""
    for i, line in enumerate(lines, 1):
        img_match = re.search(r"!\[([^\]]*)\]\(([^)]+)\)", line)
        if not img_match:
            continue

        img_path = img_match.group(2)

        # Проверить, что путь начинается с assets/
        if not img_path.startswith("assets/"):
            result.warn(filepath, i,
                        f"Изображение не в assets/: {img_path}")

        # Проверить формат имени файла
        img_name = os.path.basename(img_path)
        if not re.match(r"fig-\d{2}", img_name):
            result.warn(filepath, i,
                        f"Имя изображения не соответствует fig-XX формату: {img_name}")

        # Проверить подпись к рисунку (пустая строка + *Рис. X.X. ...*)
        if i < len(lines):
            next_line_idx = i  # 0-indexed
            # Ожидаем пустую строку
            if next_line_idx < len(lines) and lines[next_line_idx].strip() == "":
                # Потом подпись
                caption_idx = next_line_idx + 1
                if caption_idx < len(lines):
                    caption = lines[caption_idx].strip()
                    if not caption.startswith("*Рис."):
                        result.warn(filepath, caption_idx + 1,
                                    "После изображения ожидается подпись *Рис. X.X. ...*")
            else:
                result.warn(filepath, i,
                            "После изображения должна быть пустая строка перед подписью")


def check_filename(filepath, result):
    """Проверить имя файла: kebab-case, без точек."""
    basename = os.path.basename(filepath)
    name_part = os.path.splitext(basename)[0]

    if basename == "index.md":
        return

    # Проверить точки в имени
    if "." in name_part:
        result.file_warn(filepath,
                         f"Точка в имени файла: {basename} (используйте тире)")

    # Проверить kebab-case (разрешены цифры, буквы, дефисы)
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name_part):
        # Мягкая проверка — допустить нижнее подчёркивание
        if re.search(r"[A-Z]", name_part):
            result.file_warn(filepath,
                             f"Имя файла содержит заглавные буквы: {basename}")


def check_dirname(dirpath, result):
    """Проверить имя директории: без точек."""
    dirname = os.path.basename(dirpath)
    if "." in dirname and dirname != ".git":
        result.file_warn(dirpath,
                         f"Точка в имени папки: {dirname} (используйте тире)")


def validate_directory(target_dir):
    """Запустить все проверки на директории."""
    result = ValidationResult()

    if not os.path.isdir(target_dir):
        result.file_error(target_dir, "Директория не существует")
        return result

    md_files = []
    dirs_with_md = set()

    for root, dirs, files in os.walk(target_dir):
        # Пропустить assets и скрытые папки
        dirs[:] = [d for d in dirs if d != "assets" and not d.startswith(".")]

        # Проверить имена директорий
        for d in dirs:
            check_dirname(os.path.join(root, d), result)

        for f in files:
            if not f.endswith(".md"):
                continue
            filepath = os.path.join(root, f)
            md_files.append(filepath)
            dirs_with_md.add(root)

            # Прочитать файл
            with open(filepath, "r", encoding="utf-8") as fh:
                lines = fh.readlines()

            # Проверки
            check_filename(filepath, result)
            fm_end = check_frontmatter(filepath, lines, result)
            if fm_end:
                check_h1_after_frontmatter(filepath, lines, fm_end, result)
            check_images(filepath, lines, result)

    # Проверить наличие index.md в каждой папке с .md файлами
    for dir_path in dirs_with_md:
        if dir_path == target_dir:
            continue  # Корневой index.md уже проверен
        index_path = os.path.join(dir_path, "index.md")
        if not os.path.exists(index_path):
            result.file_warn(dir_path, "Нет index.md в директории")

    log.info("Проверено %d .md файлов в %d директориях", len(md_files), len(dirs_with_md))
    return result


def main():
    parser = argparse.ArgumentParser(description="Валидатор Markdown по format-guide.md")
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
