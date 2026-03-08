#!/usr/bin/env python3
"""
Build release files (markdown + epub) for each course.

Each course directory becomes a single merged markdown file and an epub.
Sections are sorted by frontmatter `order`, then alphabetically.
Heading levels are shifted based on nesting depth.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml


DOCS_ROOT = Path(__file__).resolve().parent.parent.parent / "docs"
SITE_BASE_URL = "https://docs.aisystant.com"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from markdown text."""
    m = re.match(r"^---\s*\n(.*?\n)---\s*\n", text, re.DOTALL)
    if not m:
        return {}, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        data = {}
    body = text[m.end():]
    return data, body


def shift_headings(body: str, shift: int) -> str:
    """Shift all markdown headings by `shift` levels (e.g. # -> ### for shift=2)."""
    if shift <= 0:
        return body

    def replacer(m):
        hashes = m.group(1)
        new_level = min(len(hashes) + shift, 6)
        return "#" * new_level + m.group(2)

    return re.sub(r"^(#{1,6})([ \t]+.*)$", replacer, body, flags=re.MULTILINE)


def renumber_footnotes(body: str, prefix: str) -> str:
    """Add unique prefix to reference-style footnotes [^N] to avoid conflicts."""
    # Replace [^identifier] references (both in text and definitions)
    body = re.sub(r"\[\^([^\]]+)\]", rf"[^{prefix}_\1]", body)
    return body


def resolve_image_path(img_path: str, md_file: Path, for_epub: bool = False) -> str:
    """Convert image path to absolute URL or local filesystem path."""
    if img_path.startswith("http://") or img_path.startswith("https://"):
        return img_path

    if img_path.startswith("/"):
        # Root-relative: /ru/personal/course/0.png -> docs/public/ru/...
        if for_epub:
            local = DOCS_ROOT / "public" / img_path.lstrip("/")
            return str(local) if local.exists() else f"{SITE_BASE_URL}{img_path}"
        return f"{SITE_BASE_URL}{img_path}"

    # Relative path like ./assets/fig-01.png
    md_dir = md_file.parent
    resolved = (md_dir / img_path).resolve()
    if for_epub:
        return str(resolved) if resolved.exists() else img_path
    try:
        rel = resolved.relative_to(DOCS_ROOT)
        return f"{SITE_BASE_URL}/{rel}"
    except ValueError:
        return img_path


def fix_images(body: str, md_file: Path, for_epub: bool = False) -> str:
    """Replace image references with absolute URLs or local paths."""
    def replacer(m):
        alt = m.group(1)
        path = m.group(2)
        resolved = resolve_image_path(path, md_file, for_epub)
        return f"![{alt}]({resolved})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replacer, body)


def get_last_commit_date(directory: Path) -> str:
    """Get the date of the last commit that touched this directory."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(directory)],
            capture_output=True, text=True, cwd=DOCS_ROOT.parent,
        )
        date = result.stdout.strip()
        if date:
            return date
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return "unknown"


def collect_tree(directory: Path, depth: int = 0) -> list[dict]:
    """
    Recursively collect content tree from a directory.

    Returns a sorted list of items, each with:
      - order: int
      - title: str (from H1 in content, fallback to frontmatter title)
      - body: str (content without frontmatter and first H1)
      - depth: int
      - children: list (for directories with sub-items)
      - source_file: Path
    """
    items = []

    if not directory.is_dir():
        return items

    entries = sorted(directory.iterdir())

    # Separate files and directories
    md_files = []
    subdirs = []

    for entry in entries:
        if entry.is_dir():
            if entry.name in ("assets", ".vitepress") or entry.name.startswith("."):
                continue
            subdirs.append(entry)
        elif entry.is_file() and entry.suffix == ".md" and entry.name != "index.md":
            md_files.append(entry)

    # Process index.md of this directory (if exists and depth > 0)
    index_file = directory / "index.md"
    dir_order = 0
    dir_title = directory.name
    dir_body = ""
    if index_file.exists():
        text = index_file.read_text(encoding="utf-8")
        data, body = parse_frontmatter(text)
        dir_order = data.get("order", 0) or 0
        # Extract H1 from body as title
        h1_match = re.match(r"^\s*#\s+(.+)$", body.strip(), re.MULTILINE)
        if h1_match:
            dir_title = h1_match.group(1).strip()
            # Remove the first H1 from body
            body = re.sub(r"^\s*#\s+.+\n*", "", body.strip(), count=1)
        else:
            dir_title = data.get("title", directory.name)
        dir_body = body.strip()

    # Process markdown files in this directory
    file_items = []
    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        data, body = parse_frontmatter(text)
        order = data.get("order", 0) or 0

        # Extract H1 from body as title
        h1_match = re.match(r"^\s*#\s+(.+)$", body.strip(), re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
            body = re.sub(r"^\s*#\s+.+\n*", "", body.strip(), count=1)
        else:
            title = data.get("title", md_file.stem)

        file_items.append({
            "order": order,
            "title": title,
            "body": body.strip(),
            "depth": depth + 1,
            "children": [],
            "source_file": md_file,
        })

    # Process subdirectories
    dir_items = []
    for subdir in subdirs:
        children = collect_tree(subdir, depth + 1)
        # Read subdir's index.md for ordering
        sub_index = subdir / "index.md"
        sub_order = 0
        sub_title = subdir.name
        sub_body = ""
        if sub_index.exists():
            text = sub_index.read_text(encoding="utf-8")
            data, body = parse_frontmatter(text)
            sub_order = data.get("order", 0) or 0
            h1_match = re.match(r"^\s*#\s+(.+)$", body.strip(), re.MULTILINE)
            if h1_match:
                sub_title = h1_match.group(1).strip()
                body = re.sub(r"^\s*#\s+.+\n*", "", body.strip(), count=1)
            else:
                sub_title = data.get("title", subdir.name)
            sub_body = body.strip()

        dir_items.append({
            "order": sub_order,
            "title": sub_title,
            "body": sub_body,
            "depth": depth + 1,
            "children": children,
            "source_file": sub_index if sub_index.exists() else subdir,
        })

    # Merge file items and dir items, sort by order then title
    all_items = file_items + dir_items
    all_items.sort(key=lambda x: (x["order"], x["title"]))

    return all_items


def render_tree(items: list[dict], for_epub: bool = False,
                file_counter: list[int] | None = None) -> str:
    """Render the collected tree into a single markdown string."""
    if file_counter is None:
        file_counter = [0]

    parts = []

    for item in items:
        depth = item["depth"]
        title = item["title"]
        body = item["body"]
        source_file = item["source_file"]

        # Increment file counter for footnote prefixing
        file_counter[0] += 1
        prefix = f"f{file_counter[0]:03d}"

        # Create heading at appropriate level
        heading_level = min(depth + 1, 6)  # depth 0 -> H1, depth 1 -> H2, etc.
        heading = f"{'#' * heading_level} {title}"
        parts.append(heading)

        if body:
            # Shift headings in body content
            processed = shift_headings(body, depth + 1)
            # Fix footnotes
            processed = renumber_footnotes(processed, prefix)
            # Fix image URLs
            if isinstance(source_file, Path) and source_file.is_file():
                processed = fix_images(processed, source_file, for_epub)
            parts.append(processed)

        # Process children
        if item["children"]:
            child_text = render_tree(item["children"], for_epub, file_counter)
            parts.append(child_text)

    return "\n\n".join(parts)


def build_course_markdown(course_dir: Path, for_epub: bool = False) -> str:
    """Build a single merged markdown for a course."""
    # Read course-level index.md
    index_file = course_dir / "index.md"
    course_title = course_dir.name
    course_body = ""

    course_author = "Unknown"
    course_description = ""

    if index_file.exists():
        text = index_file.read_text(encoding="utf-8")
        data, body = parse_frontmatter(text)
        course_author = data.get("author", "Unknown")
        course_description = data.get("description", "")
        h1_match = re.match(r"^\s*#\s+(.+)$", body.strip(), re.MULTILINE)
        if h1_match:
            course_title = h1_match.group(1).strip()
            body = re.sub(r"^\s*#\s+.+\n*", "", body.strip(), count=1)
        else:
            course_title = data.get("title", course_dir.name)
        course_body = body.strip()

    # Collect all content
    items = collect_tree(course_dir, depth=0)

    # Build output
    parts = [f"# {course_title}"]
    if course_body:
        course_body = fix_images(course_body, index_file, for_epub)
        parts.append(course_body)

    rendered = render_tree(items, for_epub)
    if rendered:
        parts.append(rendered)

    return "\n\n".join(parts) + "\n", course_title, course_author, course_description


def prepare_epub_markdown(md_content: str) -> str:
    """Remove the top-level H1 and shift all headings up by one level for epub."""
    lines = md_content.split("\n")
    result = []
    skipped_h1 = False
    for line in lines:
        if not skipped_h1 and re.match(r"^# ", line):
            # Skip the first H1 — it becomes the epub title via metadata
            skipped_h1 = True
            continue
        # Shift headings: ## -> #, ### -> ##, etc.
        m = re.match(r"^(#{2,6})([ \t]+.*)$", line)
        if m:
            result.append(m.group(1)[1:] + m.group(2))
        else:
            result.append(line)
    return "\n".join(result)


def build_epub(md_file: Path, epub_file: Path, title: str, author: str,
               lang: str, date: str = "", description: str = ""):
    """Convert markdown to epub using pandoc."""
    lang_code = "ru-RU" if lang == "ru" else "en-US"
    cmd = [
        "pandoc",
        str(md_file),
        "-o", str(epub_file),
        "--metadata", f"title={title}",
        "--metadata", f"author={author}",
        "--metadata", f"lang={lang_code}",
        "--metadata", "publisher=Aisystant",
        "--toc",
        "--toc-depth=3",
        "-f", "markdown+footnotes",
    ]
    if date:
        cmd += ["--metadata", f"date={date}"]
    if description:
        cmd += ["--metadata", f"description={description}"]
    subprocess.run(cmd, check=True)


def find_courses(lang_dir: Path) -> list[Path]:
    """Find all course directories (one level below category dirs)."""
    courses = []
    if not lang_dir.is_dir():
        return courses

    for category in sorted(lang_dir.iterdir()):
        if not category.is_dir() or category.name.startswith("."):
            continue
        # Skip non-content directories
        if category.name in (".vitepress", "public"):
            continue
        for course in sorted(category.iterdir()):
            if course.is_dir() and not course.name.startswith("."):
                courses.append(course)

    return courses


def main():
    parser = argparse.ArgumentParser(description="Build release markdown and epub files")
    parser.add_argument("--lang", choices=["ru", "en", "all"], default="all",
                        help="Language to build (default: all)")
    parser.add_argument("--output", "-o", type=Path, default=Path("dist"),
                        help="Output directory (default: dist)")
    parser.add_argument("--no-epub", action="store_true",
                        help="Skip epub generation")
    parser.add_argument("--course", type=str, default=None,
                        help="Build only this course (directory name)")
    args = parser.parse_args()

    languages = ["ru", "en"] if args.lang == "all" else [args.lang]

    for lang in languages:
        lang_dir = DOCS_ROOT / lang
        if not lang_dir.is_dir():
            print(f"Skipping {lang}: directory not found")
            continue

        courses = find_courses(lang_dir)

        for course_dir in courses:
            if args.course and course_dir.name != args.course:
                continue

            course_name = course_dir.name
            last_date = get_last_commit_date(course_dir)
            # Category is the parent directory name
            category = course_dir.parent.name

            print(f"Building {lang}/{category}/{course_name} (last updated: {last_date})...")

            # Output directory: dist/{lang}/{category}/
            out_dir = args.output / lang / category
            out_dir.mkdir(parents=True, exist_ok=True)
            filename_base = f"{course_name}-{lang}-{last_date}"

            # Build markdown with absolute URLs (for download/LLM use)
            md_content, title, author, description = build_course_markdown(
                course_dir, for_epub=False)
            md_out = out_dir / f"{filename_base}.md"
            md_out.write_text(md_content, encoding="utf-8")
            print(f"  -> {md_out}")

            if not args.no_epub:
                # Build separate markdown with local image paths for epub
                epub_md_content, _, _, _ = build_course_markdown(
                    course_dir, for_epub=True)
                epub_md_content = prepare_epub_markdown(epub_md_content)
                epub_md = out_dir / f"{filename_base}.epub.md"
                epub_md.write_text(epub_md_content, encoding="utf-8")

                epub_out = out_dir / f"{filename_base}.epub"
                try:
                    build_epub(epub_md, epub_out, title, author, lang,
                               date=last_date, description=description)
                    print(f"  -> {epub_out}")
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    print(f"  WARN: epub build failed: {e}", file=sys.stderr)
                finally:
                    epub_md.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
