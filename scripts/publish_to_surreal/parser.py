"""
Markdown documentation parser.

Parses the VitePress documentation structure and extracts:
    - Guides (courses) from top-level directories
    - Sections (pages) from markdown files
    - Metadata from YAML frontmatter

Language Support:
    - Currently processes only Russian content (docs/ru/)
    - The `lang` field is set to "ru" for all extracted items
    - To add English support, call parse_docs() with lang="en" and base_path="docs/en"

Directory Structure Expected:
    docs/
    └── ru/
        ├── personal/
        │   ├── systems-thinking-introduction/
        │   │   ├── index.md
        │   │   ├── section-1/
        │   │   │   ├── index.md
        │   │   │   └── page1.md
        │   │   └── page2.md
        │   └── another-course/
        ├── professional/
        └── research/
"""

import os
import re
import logging
from pathlib import Path
from typing import Generator
from datetime import datetime

import yaml

from models import Guide, Section, Chunk
from chunker import chunk_markdown, ChunkData


logger = logging.getLogger(__name__)

# Categories in the documentation
CATEGORIES = ["personal", "professional", "research"]


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from markdown content.

    Args:
        content: Full markdown file content

    Returns:
        Tuple of (frontmatter_dict, remaining_content)

    Example:
        Input:
            '''
            ---
            title: "My Title"
            order: 5
            ---
            # Content here
            '''
        Output:
            ({"title": "My Title", "order": 5}, "# Content here")
    """
    frontmatter = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                # Try to extract title manually if YAML fails (nested quotes issue)
                frontmatter = _extract_frontmatter_fallback(parts[1])
            body = parts[2].strip()

    return frontmatter, body


def _extract_frontmatter_fallback(yaml_str: str) -> dict:
    """
    Fallback frontmatter extraction when YAML parsing fails.

    Handles cases like nested quotes in title.
    """
    result = {}

    for line in yaml_str.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('title:'):
            # Extract everything after 'title:'
            title = line[6:].strip()
            # Remove outer quotes if present
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            elif title.startswith("'") and title.endswith("'"):
                title = title[1:-1]
            result['title'] = title

        elif line.startswith('order:'):
            try:
                result['order'] = int(line[6:].strip())
            except ValueError:
                pass

    return result


def get_guide_order(guide_slug: str, category: str) -> int:
    """
    Determine guide order based on known course ordering.

    This is a simple heuristic; could be enhanced with a config file.
    """
    order_map = {
        "personal": {
            "systems-thinking-introduction": 1,
            "self-development-methods": 2,
            "systems-self-development": 3,
            "systems-based-fitness": 4,
        },
        "professional": {
            "rational-work": 1,
            "systems-thinking": 2,
            "methodology": 3,
            "systems-engineering": 4,
            "personality-engineering": 5,
            "systems-management": 6,
        },
        "research": {
            "intellect-stack": 1,
        },
    }

    return order_map.get(category, {}).get(guide_slug, 99)


def parse_guide(guide_path: Path, category: str, lang: str = "ru") -> Guide | None:
    """
    Parse a guide directory and extract metadata.

    Args:
        guide_path: Path to guide directory
        category: Category name (personal, professional, research)
        lang: Language code

    Returns:
        Guide object or None if invalid
    """
    index_path = guide_path / "index.md"
    if not index_path.exists():
        logger.warning(f"No index.md found in {guide_path}")
        return None

    content = index_path.read_text(encoding="utf-8")
    frontmatter, _ = parse_frontmatter(content)

    slug = guide_path.name
    title = frontmatter.get("title", slug.replace("-", " ").title())

    return Guide(
        slug=slug,
        title=title,
        category=category,
        lang=lang,
        order=get_guide_order(slug, category),
        updated_at=datetime.fromtimestamp(index_path.stat().st_mtime),
    )


def iter_markdown_files(guide_path: Path) -> Generator[Path, None, None]:
    """
    Iterate over all markdown files in a guide directory.

    Yields files in order suitable for processing:
        1. index.md files first (if in subdirectories)
        2. Regular .md files sorted by name

    Args:
        guide_path: Path to guide directory

    Yields:
        Path objects for each markdown file
    """
    for root, dirs, files in os.walk(guide_path):
        root_path = Path(root)

        # Sort files, putting index.md first
        md_files = sorted(
            [f for f in files if f.endswith('.md')],
            key=lambda x: (x != 'index.md', x)
        )

        for filename in md_files:
            file_path = root_path / filename

            # Skip the guide's own index.md (already processed)
            if file_path == guide_path / "index.md":
                continue

            yield file_path


def parse_section(
    file_path: Path,
    guide: Guide,
    guide_path: Path,
    docs_root: Path,
    section_order: int
) -> Section:
    """
    Parse a markdown file into a Section.

    Args:
        file_path: Path to markdown file
        guide: Parent guide
        guide_path: Path to guide directory (for calculating relative path)
        docs_root: Root docs directory (for URL calculation)
        section_order: Order within guide

    Returns:
        Section object
    """
    content = file_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    # Calculate slug from full relative path within guide directory
    # This ensures unique slugs for files in any nested subdirectories
    # e.g., "01-physical-world/11-summary.md" -> "01-physical-world_11-summary"
    # e.g., "a/b/c/file.md" -> "a_b_c_file"
    relative_to_guide = file_path.relative_to(guide_path)

    if file_path.stem == "index":
        # For index files, use parent directory path
        # e.g., "01-physical-world/index.md" -> "01-physical-world"
        slug = str(relative_to_guide.parent).replace("/", "_").replace("\\", "_")
    else:
        # Use full path without extension, replacing / with _
        slug = str(relative_to_guide.with_suffix("")).replace("/", "_").replace("\\", "_")

    # Calculate full URL path
    relative_path = file_path.relative_to(docs_root)
    # Remove .md extension and convert to URL
    url_path = "/" + str(relative_path.with_suffix("")).replace("\\", "/")

    # Get order from frontmatter or use provided order
    order = frontmatter.get("order", section_order)

    return Section(
        slug=slug,
        guide_id=guide.id,
        title=frontmatter.get("title", slug.replace("-", " ").title()),
        url=url_path,
        content=content,  # Store full content including frontmatter
        lang=guide.lang,
        order=order,
        updated_at=datetime.fromtimestamp(file_path.stat().st_mtime),
    )


def create_chunks(section: Section) -> list[Chunk]:
    """
    Create searchable chunks from a section.

    Args:
        section: Section to chunk

    Returns:
        List of Chunk objects
    """
    # Parse out the body (without frontmatter)
    _, body = parse_frontmatter(section.content)

    chunk_data_list = chunk_markdown(body)

    return [
        Chunk(
            section_id=section.id,
            guide_id=section.guide_id,
            heading=cd.heading,
            content=cd.content,
            chunk_index=cd.chunk_index,
            lang=section.lang,
        )
        for cd in chunk_data_list
    ]


def parse_docs(
    docs_root: Path,
    lang: str = "ru"
) -> Generator[tuple[Guide, list[Section], list[Chunk]], None, None]:
    """
    Parse entire documentation structure.

    This is the main entry point for parsing docs.

    Args:
        docs_root: Root docs directory (e.g., Path("docs"))
        lang: Language code to process ("ru" or "en")

    Yields:
        Tuples of (guide, sections, chunks) for each guide

    Example:
        ```python
        for guide, sections, chunks in parse_docs(Path("docs"), lang="ru"):
            print(f"Guide: {guide.title}")
            print(f"  Sections: {len(sections)}")
            print(f"  Chunks: {len(chunks)}")
        ```

    Language Support Note:
        Currently only "ru" is fully supported. To add English:
        1. Ensure docs/en/ has the same structure as docs/ru/
        2. Call parse_docs(docs_root, lang="en")
    """
    lang_path = docs_root / lang

    if not lang_path.exists():
        logger.error(f"Language directory not found: {lang_path}")
        return

    for category in CATEGORIES:
        category_path = lang_path / category

        if not category_path.exists():
            logger.debug(f"Category not found: {category_path}")
            continue

        # Iterate over guide directories
        for guide_dir in sorted(category_path.iterdir()):
            if not guide_dir.is_dir():
                continue

            guide = parse_guide(guide_dir, category, lang)
            if not guide:
                continue

            logger.info(f"Processing guide: {guide.title}")

            sections = []
            all_chunks = []
            section_order = 0

            for md_file in iter_markdown_files(guide_dir):
                section = parse_section(md_file, guide, guide_dir, docs_root, section_order)
                sections.append(section)

                chunks = create_chunks(section)
                all_chunks.extend(chunks)

                section_order += 1
                logger.debug(f"  Section: {section.title} ({len(chunks)} chunks)")

            # Sort sections by URL path (files are named with numeric prefixes)
            sections.sort(key=lambda s: s.url)

            yield guide, sections, all_chunks
