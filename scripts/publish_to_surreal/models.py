"""
Data models for SurrealDB documentation storage.

Language Support:
    - All models include a `lang` field to support multi-language content
    - Currently only Russian (ru) content is processed
    - English (en) support can be added by extending the parser to process docs/en/
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of content for change detection."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


@dataclass
class Guide:
    """
    Represents a documentation guide/course.

    Examples:
        - systems-thinking-introduction
        - rational-work
        - intellect-stack

    Attributes:
        id: Unique identifier (e.g., "guide:systems-thinking-introduction")
        slug: URL-friendly identifier
        title: Human-readable title
        category: One of "personal", "professional", "research"
        lang: Language code ("ru" or "en")
        order: Sort order within category
        updated_at: Last modification timestamp
    """
    slug: str
    title: str
    category: str
    lang: str = "ru"
    order: int = 0
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def id(self) -> str:
        return f"guides:{self.lang}_{self.slug}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "category": self.category,
            "lang": self.lang,
            "order": self.order,
            "updated_at": self.updated_at,  # Pass datetime directly, surrealdb lib handles it
        }


@dataclass
class Section:
    """
    Represents a single documentation page/section (one markdown file).

    Attributes:
        slug: URL-friendly identifier (filename without .md)
        guide_id: Reference to parent guide
        title: Human-readable title from frontmatter
        url: Full URL path (e.g., "/ru/personal/systems-thinking-introduction/word-object-system")
        content: Full markdown content
        content_hash: SHA-256 hash of content for change detection
        lang: Language code ("ru" or "en")
        order: Sort order within guide (from frontmatter)
        updated_at: Last modification timestamp
    """
    slug: str
    guide_id: str
    title: str
    url: str
    content: str
    lang: str = "ru"
    order: int = 0
    content_hash: str = ""
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        # Auto-compute hash if not provided
        if not self.content_hash and self.content:
            self.content_hash = compute_content_hash(self.content)

    @property
    def id(self) -> str:
        # Create unique ID from guide and slug
        guide_slug = self.guide_id.split(":")[-1]
        return f"sections:{guide_slug}_{self.slug}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "slug": self.slug,
            "guide_id": self.guide_id,
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "content_hash": self.content_hash,
            "lang": self.lang,
            "order": self.order,
            "updated_at": self.updated_at,  # Pass datetime directly, surrealdb lib handles it
        }


@dataclass
class Chunk:
    """
    Represents a searchable text chunk with vector embedding.

    Chunking Strategy:
        1. Split content by headings (h1-h6)
        2. If chunk > 200 chars, split by sentences using sliding window
        3. Each chunk gets an embedding vector for semantic search

    Attributes:
        section_id: Reference to parent section
        guide_id: Reference to parent guide (denormalized for query efficiency)
        heading: Parent heading text (if any)
        content: Chunk text content
        chunk_index: Position within section (for ordering)
        lang: Language code ("ru" or "en")
        embedding: Vector embedding for semantic search (1536 dims for OpenAI)
    """
    section_id: str
    guide_id: str
    heading: Optional[str]
    content: str
    chunk_index: int
    lang: str = "ru"
    embedding: Optional[list[float]] = None

    @property
    def id(self) -> str:
        section_slug = self.section_id.split(":")[-1]
        return f"chunks:{section_slug}_{self.chunk_index}"

    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "section_id": self.section_id,
            "guide_id": self.guide_id,
            "heading": self.heading,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "lang": self.lang,
        }
        if self.embedding:
            result["embedding"] = self.embedding
        return result
