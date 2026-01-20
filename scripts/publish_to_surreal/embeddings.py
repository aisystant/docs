"""
OpenAI embeddings generation for semantic search.

Uses OpenAI's text-embedding-3-small model (1536 dimensions) for generating
vector embeddings from text chunks.

Environment Variables:
    OPENAI_API_KEY: Required. Your OpenAI API key.

Usage:
    ```python
    from embeddings import generate_embeddings

    chunks = [chunk1, chunk2, chunk3]
    chunks_with_embeddings = generate_embeddings(chunks, batch_size=100)
    ```
"""

import os
import logging
from typing import Sequence

from openai import OpenAI

from models import Chunk


logger = logging.getLogger(__name__)

# OpenAI embedding model configuration
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
MAX_BATCH_SIZE = 2048  # OpenAI limit


def get_openai_client() -> OpenAI:
    """
    Create OpenAI client from environment.

    Returns:
        OpenAI client instance

    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    return OpenAI(api_key=api_key)


def create_embedding_text(chunk: Chunk) -> str:
    """
    Create text for embedding from a chunk.

    Combines heading and content for better semantic representation.

    Args:
        chunk: Chunk to create embedding text for

    Returns:
        Text string for embedding
    """
    if chunk.heading:
        return f"{chunk.heading}\n\n{chunk.content}"
    return chunk.content


def generate_embeddings_batch(
    client: OpenAI,
    texts: list[str]
) -> list[list[float]]:
    """
    Generate embeddings for a batch of texts.

    Args:
        client: OpenAI client
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    # Sort by index to maintain order
    sorted_data = sorted(response.data, key=lambda x: x.index)
    return [item.embedding for item in sorted_data]


def generate_embeddings(
    chunks: Sequence[Chunk],
    batch_size: int = 100
) -> list[Chunk]:
    """
    Generate embeddings for all chunks.

    Processes chunks in batches for efficiency and to avoid rate limits.

    Args:
        chunks: Sequence of chunks to generate embeddings for
        batch_size: Number of chunks to process in each API call

    Returns:
        New list of chunks with embeddings populated

    Example:
        ```python
        chunks = [Chunk(...), Chunk(...), ...]
        chunks_with_embeddings = generate_embeddings(chunks)

        for chunk in chunks_with_embeddings:
            print(f"Embedding dim: {len(chunk.embedding)}")  # 1536
        ```
    """
    if not chunks:
        return []

    client = get_openai_client()
    result_chunks = []

    # Process in batches
    total_batches = (len(chunks) + batch_size - 1) // batch_size

    for batch_idx in range(0, len(chunks), batch_size):
        batch = chunks[batch_idx:batch_idx + batch_size]
        current_batch = batch_idx // batch_size + 1

        logger.info(f"Generating embeddings batch {current_batch}/{total_batches} "
                   f"({len(batch)} chunks)")

        # Prepare texts for embedding
        texts = [create_embedding_text(chunk) for chunk in batch]

        # Generate embeddings
        embeddings = generate_embeddings_batch(client, texts)

        # Create new chunks with embeddings
        for chunk, embedding in zip(batch, embeddings):
            new_chunk = Chunk(
                section_id=chunk.section_id,
                guide_id=chunk.guide_id,
                heading=chunk.heading,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                lang=chunk.lang,
                embedding=embedding,
            )
            result_chunks.append(new_chunk)

    logger.info(f"Generated {len(result_chunks)} embeddings")
    return result_chunks


def generate_single_embedding(chunk: Chunk) -> Chunk:
    """
    Generate embedding for a single chunk.

    Use this for step-by-step processing (embed → write → next).

    Args:
        chunk: Chunk to generate embedding for

    Returns:
        New Chunk with embedding populated
    """
    client = get_openai_client()
    text = create_embedding_text(chunk)

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return Chunk(
        section_id=chunk.section_id,
        guide_id=chunk.guide_id,
        heading=chunk.heading,
        content=chunk.content,
        chunk_index=chunk.chunk_index,
        lang=chunk.lang,
        embedding=response.data[0].embedding,
    )


def generate_query_embedding(query: str) -> list[float]:
    """
    Generate embedding for a search query.

    Use this when performing semantic search.

    Args:
        query: Search query text

    Returns:
        Embedding vector (1536 dimensions)

    Example:
        ```python
        query_embedding = generate_query_embedding("What is systems thinking?")
        # Use query_embedding for vector similarity search in SurrealDB
        ```
    """
    client = get_openai_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )

    return response.data[0].embedding
