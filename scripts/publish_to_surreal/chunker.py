"""
Chunking logic for splitting markdown content into searchable chunks.

Chunking Strategy:
    1. Split content by headings (h1-h6 in markdown: # to ######)
    2. If a chunk exceeds MAX_CHUNK_SIZE (200 chars), split by sentences
    3. Sentence splitting uses a sliding window to maintain context overlap

This approach ensures:
    - Semantic coherence (chunks align with document structure)
    - Reasonable chunk sizes for embedding models
    - Context preservation through overlapping windows
"""

import re
from dataclasses import dataclass
from typing import Optional


MAX_CHUNK_SIZE = 1000  # Maximum characters before splitting by sentences
SENTENCE_OVERLAP = 2   # Number of sentences to overlap in sliding window


@dataclass
class ChunkData:
    """Raw chunk data before conversion to Chunk model."""
    heading: Optional[str]
    content: str
    chunk_index: int


def split_by_headings(markdown: str) -> list[tuple[Optional[str], str]]:
    """
    Split markdown content by headings.

    Args:
        markdown: Full markdown content

    Returns:
        List of (heading, content) tuples. First item may have heading=None
        if content precedes the first heading.

    Example:
        Input:
            '''
            Intro text
            # Heading 1
            Content 1
            ## Heading 2
            Content 2
            '''
        Output:
            [(None, "Intro text"), ("Heading 1", "Content 1"), ("Heading 2", "Content 2")]
    """
    # Pattern matches markdown headings (# to ######)
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    chunks = []
    last_end = 0
    current_heading = None

    for match in heading_pattern.finditer(markdown):
        # Content before this heading belongs to previous section
        content_before = markdown[last_end:match.start()].strip()
        if content_before or current_heading:
            chunks.append((current_heading, content_before))

        current_heading = match.group(2).strip()
        last_end = match.end()

    # Don't forget content after the last heading
    remaining_content = markdown[last_end:].strip()
    if remaining_content or current_heading:
        chunks.append((current_heading, remaining_content))

    # Filter out empty chunks
    return [(h, c) for h, c in chunks if c]


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences.

    Handles common sentence-ending punctuation including:
    - Period, exclamation, question mark
    - Cyrillic text (Russian)
    - Abbreviations (tries to avoid splitting on them)

    Args:
        text: Text to split

    Returns:
        List of sentences
    """
    # Split on sentence-ending punctuation followed by space and capital letter
    # This pattern handles both Latin and Cyrillic
    sentence_pattern = re.compile(r'(?<=[.!?])\s+(?=[A-ZА-ЯЁ])')

    sentences = sentence_pattern.split(text)

    # Clean up and filter empty sentences
    return [s.strip() for s in sentences if s.strip()]


def sliding_window_chunks(sentences: list[str], max_size: int = MAX_CHUNK_SIZE,
                          overlap: int = SENTENCE_OVERLAP) -> list[str]:
    """
    Create chunks from sentences using a sliding window approach.

    Args:
        sentences: List of sentences
        max_size: Maximum chunk size in characters
        overlap: Number of sentences to overlap between chunks

    Returns:
        List of text chunks
    """
    if not sentences:
        return []

    chunks = []
    current_chunk = []
    current_size = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        # If single sentence exceeds max, it becomes its own chunk
        if sentence_len > max_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
            chunks.append(sentence)
            continue

        # Check if adding this sentence would exceed max size
        if current_size + sentence_len + 1 > max_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            # Keep last `overlap` sentences for context
            current_chunk = current_chunk[-overlap:] if overlap > 0 else []
            current_size = sum(len(s) for s in current_chunk) + len(current_chunk) - 1

        current_chunk.append(sentence)
        current_size += sentence_len + 1  # +1 for space

    # Don't forget the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def chunk_markdown(markdown: str) -> list[ChunkData]:
    """
    Main chunking function: splits markdown into searchable chunks.

    Strategy:
        1. Split by headings to maintain semantic structure
        2. For chunks > MAX_CHUNK_SIZE, split by sentences with overlap
        3. Preserve heading association for context

    Args:
        markdown: Full markdown content

    Returns:
        List of ChunkData objects ready for embedding
    """
    heading_chunks = split_by_headings(markdown)
    result = []
    chunk_index = 0

    for heading, content in heading_chunks:
        # Remove markdown formatting for cleaner text
        clean_content = clean_markdown(content)

        if len(clean_content) <= MAX_CHUNK_SIZE:
            # Chunk is small enough, keep as is
            result.append(ChunkData(
                heading=heading,
                content=clean_content,
                chunk_index=chunk_index
            ))
            chunk_index += 1
        else:
            # Split by sentences using sliding window
            sentences = split_into_sentences(clean_content)
            sub_chunks = sliding_window_chunks(sentences)

            for sub_chunk in sub_chunks:
                result.append(ChunkData(
                    heading=heading,
                    content=sub_chunk,
                    chunk_index=chunk_index
                ))
                chunk_index += 1

    return result


def clean_markdown(text: str) -> str:
    """
    Remove markdown formatting to get plain text.

    Removes:
        - Image references ![...](...)
        - Links but keeps text [text](url) -> text
        - Bold/italic markers
        - Code blocks
        - Horizontal rules
        - HTML tags

    Args:
        text: Markdown text

    Returns:
        Clean plain text
    """
    # Remove images
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)

    # Convert links to just text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)

    # Remove bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)

    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\*\*\*+$', '', text, flags=re.MULTILINE)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove footnote references
    text = re.sub(r'\[\^[^\]]+\]', '', text)

    # Normalize whitespace
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()
