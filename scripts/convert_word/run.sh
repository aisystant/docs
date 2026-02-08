#!/bin/bash
#
# Word→Markdown конвертер
#
# Использование:
#   ./run.sh <input.docx> <output_dir> [--course-title "Название"]
#
# Примеры:
#   ./run.sh sources/word-files/file.docx sources/converted/systems-thinking-introduction
#   ./run.sh sources/word-files/file.docx sources/converted/my-course --course-title "Мой курс"
#
# Зависимости:
#   - pandoc (brew install pandoc)
#   - Python 3 + transliterate (pip3 install -r requirements.txt)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Проверка аргументов
if [ $# -lt 2 ]; then
    echo "Использование: $0 <input.docx> <output_dir> [--course-title \"Название\"]"
    echo ""
    echo "Примеры:"
    echo "  $0 sources/word-files/file.docx sources/converted/course-name"
    echo "  $0 sources/word-files/file.docx sources/converted/course-name --course-title \"Мой курс\""
    exit 1
fi

INPUT="$1"
OUTPUT="$2"
shift 2

# Проверка pandoc
if ! command -v pandoc &> /dev/null; then
    echo "ОШИБКА: pandoc не установлен. Установите: brew install pandoc"
    exit 1
fi

# Проверка Python-зависимостей
if ! python3 -c "import transliterate" 2>/dev/null; then
    echo "Устанавливаю Python-зависимости..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
fi

# Определить абсолютные пути (если относительные — от корня репо)
if [[ ! "$INPUT" = /* ]]; then
    INPUT="$REPO_ROOT/$INPUT"
fi
if [[ ! "$OUTPUT" = /* ]]; then
    OUTPUT="$REPO_ROOT/$OUTPUT"
fi

# Проверка входного файла
if [ ! -f "$INPUT" ]; then
    echo "ОШИБКА: Файл не найден: $INPUT"
    exit 1
fi

echo "========================================"
echo "Word→Markdown конвертация"
echo "========================================"
echo "Вход:  $INPUT"
echo "Выход: $OUTPUT"
echo ""

# Этап 1+2: Конвертация и разбивка
echo "--- Этап 1: Конвертация и разбивка ---"
python3 "$SCRIPT_DIR/convert.py" "$INPUT" "$OUTPUT" "$@"

# Этап 3: Валидация
echo ""
echo "--- Этап 2: Валидация ---"
python3 "$SCRIPT_DIR/validate.py" "$OUTPUT"

echo ""
echo "========================================"
echo "Готово! Результат: $OUTPUT"
echo "========================================"
