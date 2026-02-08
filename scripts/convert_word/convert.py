#!/usr/bin/env python3
"""
Word→Markdown конвертер.

Конвертирует .docx файл в структурированные .md файлы
по правилам format-guide.md.

Использование:
    python3 convert.py <input.docx> <output_dir> [--course-slug NAME]

Пример:
    python3 convert.py sources/word-files/file.docx sources/converted/systems-thinking-introduction
"""

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    from transliterate import translit
except ImportError:
    print("Установите зависимости: pip3 install -r requirements.txt")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def slugify(text):
    """Русский текст → kebab-case slug."""
    # Убрать номер раздела в начале (например "1. " или "1.2. ")
    text_clean = re.sub(r"^\d+(\.\d+)*\.?\s*", "", text)
    try:
        latin = translit(text_clean, "ru", reversed=True)
    except Exception:
        latin = text_clean
    # Оставить только буквы, цифры, пробелы и дефисы
    latin = re.sub(r"[^\w\s-]", "", latin)
    latin = re.sub(r"[\s_]+", "-", latin.strip())
    latin = re.sub(r"-+", "-", latin)
    return latin.lower().strip("-")[:60]


def run_pandoc(docx_path, work_dir):
    """Запустить pandoc для конвертации .docx → .md + извлечение медиа."""
    raw_md = os.path.join(work_dir, "raw.md")
    media_dir = os.path.join(work_dir, "media")
    cmd = [
        "pandoc", docx_path,
        "-t", "markdown",
        "--wrap=none",
        f"--extract-media={media_dir}",
        "-o", raw_md,
    ]
    log.info("Запуск pandoc: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log.error("pandoc ошибка: %s", result.stderr)
        sys.exit(1)
    log.info("pandoc завершён, raw.md: %d строк", sum(1 for _ in open(raw_md)))
    return raw_md, media_dir


def clean_pandoc_attrs(line):
    """Убрать pandoc-атрибуты {width=... height=...} из строк."""
    return re.sub(r"\{[^}]*width[^}]*\}", "", line)


def extract_footnotes(lines):
    """
    Извлечь определения сносок из списка строк.

    Pandoc помещает все определения сносок в конец файла.
    Возвращает (lines_without_footnotes, footnotes_dict).
    footnotes_dict: {"1": "[^1]: текст сноски\n", ...}
    """
    footnotes = {}
    content_lines = []
    i = 0
    while i < len(lines):
        fn_match = re.match(r"^\[\^(\d+)\]:\s*(.*)", lines[i])
        if fn_match:
            fn_id = fn_match.group(1)
            fn_lines = [lines[i]]
            i += 1
            # Многострочные сноски: продолжение с отступом
            while i < len(lines) and (lines[i].startswith("    ") or lines[i].strip() == ""):
                fn_lines.append(lines[i])
                i += 1
                if lines[i - 1].strip() == "" and i < len(lines) and not lines[i].startswith("    "):
                    break
            footnotes[fn_id] = "".join(fn_lines)
        else:
            content_lines.append(lines[i])
            i += 1
    return content_lines, footnotes


def parse_sections(raw_md_path):
    """
    Разбить raw.md на секции по H1 и подразделы по H2.

    Возвращает (sections, footnotes_dict).
    """
    with open(raw_md_path, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    # Сначала извлечь все определения сносок
    lines, footnotes = extract_footnotes(all_lines)
    log.info("Извлечено %d определений сносок", len(footnotes))

    sections = []
    current_section = None
    current_subsection = None
    pre_section_lines = []

    for line in lines:
        line = clean_pandoc_attrs(line)
        h1_match = re.match(r"^# (.+)$", line)
        h2_match = re.match(r"^## (.+)$", line)

        if h1_match:
            # Сохранить предыдущую подсекцию
            if current_subsection and current_section:
                current_section["subsections"].append(current_subsection)
            elif current_subsection:
                # Подсекции до первого H1 → "предисловие"
                if not sections or sections[0].get("level") != "pre":
                    sections.insert(0, {
                        "title": "Предисловие",
                        "level": "pre",
                        "subsections": [],
                    })
                sections[0]["subsections"].append(current_subsection)

            # Сохранить предыдущую секцию
            if current_section:
                sections.append(current_section)

            title = h1_match.group(1).strip()
            current_section = {
                "title": title,
                "level": "section",
                "subsections": [],
            }
            current_subsection = None
            continue

        if h2_match:
            # Сохранить предыдущую подсекцию
            if current_subsection:
                if current_section:
                    current_section["subsections"].append(current_subsection)
                else:
                    # H2 до первого H1 → предисловие
                    if not sections or sections[0].get("level") != "pre":
                        sections.insert(0, {
                            "title": "Предисловие",
                            "level": "pre",
                            "subsections": [],
                        })
                    sections[0]["subsections"].append(current_subsection)

            title = h2_match.group(1).strip()
            current_subsection = {
                "title": title,
                "lines": [],
                "images": [],
            }
            continue

        # Обычная строка
        if current_subsection:
            current_subsection["lines"].append(line)
            # Собрать ссылки на изображения
            img_match = re.search(r"!\[([^\]]*)\]\(([^)]+)\)", line)
            if img_match:
                current_subsection["images"].append({
                    "alt": img_match.group(1),
                    "path": img_match.group(2),
                })
        elif current_section is None:
            pre_section_lines.append(line)

    # Финализация
    if current_subsection:
        if current_section:
            current_section["subsections"].append(current_subsection)
        else:
            if not sections or sections[0].get("level") != "pre":
                sections.insert(0, {
                    "title": "Предисловие",
                    "level": "pre",
                    "subsections": [],
                })
            sections[0]["subsections"].append(current_subsection)
    if current_section:
        sections.append(current_section)

    # Если были строки до любого заголовка, создать intro-подсекцию
    if pre_section_lines and any(l.strip() for l in pre_section_lines):
        if not sections or sections[0].get("level") != "pre":
            sections.insert(0, {
                "title": "Предисловие",
                "level": "pre",
                "subsections": [],
            })
        sections[0]["subsections"].insert(0, {
            "title": "Введение",
            "lines": pre_section_lines,
            "images": [],
        })

    return sections, footnotes


def determine_subsection_type(title):
    """Определить тип подраздела по заголовку."""
    title_lower = title.lower()
    if re.match(r"моделирование\s+\d+\.\d+\.\s*понятия", title_lower):
        return "table", "concepts"
    if "моделирование" in title_lower:
        return "table", "modeling"
    if "вопросы для повторения" in title_lower:
        return "checklist", "review"
    if "домашнее задание" in title_lower:
        return "checklist", "homework"
    if "задач" in title_lower:
        return "multiple_choice", "problems"
    if "выводы раздела" in title_lower:
        return "text", "summary"
    return "text", None


def make_filename(order, title, sub_type_suffix):
    """Создать имя файла: NN-slug.md"""
    slug = slugify(title)
    if sub_type_suffix:
        # Если уже есть суффикс типа в слаге, не дублировать
        if sub_type_suffix not in slug:
            slug = f"{slug}-{sub_type_suffix}" if slug else sub_type_suffix
    return f"{order:02d}-{slug}.md"


def copy_image(src_path, dest_dir, fig_number, media_base):
    """Скопировать изображение, переименовать в fig-XX-description формат."""
    # Найти исходный файл
    full_src = src_path
    if not os.path.isabs(src_path):
        full_src = os.path.join(media_base, src_path)
    # Нормализовать путь (pandoc иногда даёт media/media/imageN.png)
    if not os.path.exists(full_src):
        # Попробовать без первого media/
        alt_path = src_path.replace("media/media/", "media/")
        full_src = os.path.join(media_base, alt_path)
    if not os.path.exists(full_src):
        # Попробовать абсолютный путь как есть
        full_src = src_path
    if not os.path.exists(full_src):
        log.warning("Изображение не найдено: %s", src_path)
        return None

    ext = os.path.splitext(full_src)[1].lower()
    if not ext:
        ext = ".png"
    dest_name = f"fig-{fig_number:02d}{ext}"
    dest_path = os.path.join(dest_dir, dest_name)
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(full_src, dest_path)
    return dest_name


def write_md_file(filepath, title, content, order, doc_type="text"):
    """Записать .md файл с YAML front matter."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f'title: "{title}"\n')
        f.write(f"order: {order}\n")
        if doc_type != "index":
            f.write(f"type: {doc_type}\n")
        f.write("---\n\n\n")
        f.write(f"# {title}\n\n")
        if content:
            f.write(content)


def write_index_file(filepath, title, order):
    """Записать index.md для секции."""
    write_md_file(filepath, title, "", order, doc_type="index")


def process_subsection_content(lines, images, assets_dir, media_base, section_fig_counter, footnotes=None):
    """
    Обработать контент подраздела:
    - Скопировать и переименовать изображения
    - Обновить ссылки на изображения
    - Добавить определения сносок, на которые есть ссылки

    Возвращает обработанный текст и обновлённый счётчик рисунков.
    """
    content = "".join(lines)
    fig_counter = section_fig_counter

    # Обработать каждое изображение
    for img in images:
        fig_counter += 1
        new_name = copy_image(img["path"], assets_dir, fig_counter, media_base)
        if new_name:
            # Заменить ссылку
            old_ref = f"![{img['alt']}]({img['path']})"
            # Убрать автосгенерированные alt-тексты от Word
            clean_alt = img["alt"]
            if "Автоматически созданное описание" in clean_alt:
                clean_alt = re.sub(r"\s*Автоматически созданное описание\s*", "", clean_alt)
            if not clean_alt.strip():
                clean_alt = new_name.replace(".png", "").replace(".jpg", "").replace(".jpeg", "")

            new_ref = f"![{clean_alt}](assets/{new_name})"
            content = content.replace(old_ref, new_ref)

    # Убрать остатки pandoc-атрибутов
    content = re.sub(r"\{[^}]*width[^}]*\}", "", content)

    # Убрать лишние пустые строки (больше 2 подряд)
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    # Добавить определения сносок, на которые есть ссылки в этом подразделе
    if footnotes:
        refs = set(re.findall(r"\[\^(\d+)\](?!:)", content))
        if refs:
            fn_block = []
            for ref_id in sorted(refs, key=int):
                if ref_id in footnotes:
                    fn_block.append(footnotes[ref_id])
            if fn_block:
                content = content.rstrip() + "\n\n" + "".join(fn_block)

    return content, fig_counter


def build_output(sections, output_dir, media_base, course_title=None, footnotes=None):
    """Создать структуру папок и файлов из разобранных секций."""
    os.makedirs(output_dir, exist_ok=True)

    # Course-level index.md
    title = course_title or (sections[0]["title"] if sections else "Курс")
    write_index_file(os.path.join(output_dir, "index.md"), title, 0)

    section_order = 0
    for section in sections:
        # Определить номер папки
        if section["level"] == "pre":
            folder_name = f"{section_order:02d}-intro"
        else:
            folder_name = f"{section_order:02d}-{slugify(section['title'])}"
        section_order += 1

        section_dir = os.path.join(output_dir, folder_name)
        os.makedirs(section_dir, exist_ok=True)
        assets_dir = os.path.join(section_dir, "assets")

        # Section index.md
        write_index_file(
            os.path.join(section_dir, "index.md"),
            section["title"],
            section_order - 1,
        )

        fig_counter = 0
        for sub_order, sub in enumerate(section["subsections"]):
            doc_type, suffix = determine_subsection_type(sub["title"])
            filename = make_filename(sub_order + 1, sub["title"], suffix)
            filepath = os.path.join(section_dir, filename)

            content, fig_counter = process_subsection_content(
                sub["lines"], sub["images"], assets_dir, media_base, fig_counter, footnotes
            )

            write_md_file(filepath, sub["title"], content, sub_order + 1, doc_type)
            log.info("  → %s", os.path.relpath(filepath, output_dir))

        log.info("Раздел '%s': %d подразделов, %d изображений",
                 section["title"], len(section["subsections"]), fig_counter)


def main():
    parser = argparse.ArgumentParser(description="Word→Markdown конвертер")
    parser.add_argument("input", help="Путь к .docx файлу")
    parser.add_argument("output", help="Выходная директория (например sources/converted/course-name)")
    parser.add_argument("--course-title", help="Название курса (по умолчанию берётся из документа)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        log.error("Файл не найден: %s", args.input)
        sys.exit(1)

    if not shutil.which("pandoc"):
        log.error("pandoc не найден. Установите: brew install pandoc")
        sys.exit(1)

    # Создать временную директорию для pandoc
    with tempfile.TemporaryDirectory(prefix="word2md_") as work_dir:
        log.info("Рабочая директория: %s", work_dir)

        # Этап 1: pandoc
        raw_md, media_dir = run_pandoc(os.path.abspath(args.input), work_dir)

        # Этап 2: Парсинг
        log.info("Разбор структуры документа...")
        sections, footnotes = parse_sections(raw_md)
        log.info("Найдено %d разделов", len(sections))
        for s in sections:
            log.info("  [%s] %s (%d подразделов)",
                     s["level"], s["title"], len(s["subsections"]))

        # Этап 3: Создание структуры
        output_dir = os.path.abspath(args.output)
        if os.path.exists(output_dir):
            log.warning("Выходная директория существует, будет перезаписана: %s", output_dir)
            shutil.rmtree(output_dir)

        log.info("Создание структуры в %s ...", output_dir)
        build_output(sections, output_dir, work_dir, args.course_title, footnotes)

    log.info("Конвертация завершена: %s", args.output)


if __name__ == "__main__":
    main()
