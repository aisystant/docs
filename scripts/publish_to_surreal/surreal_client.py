"""
SurrealDB client for publishing documentation.

Handles connection to SurrealDB and CRUD operations for guides, sections, and chunks.

Environment Variables:
    SURREAL_URL: SurrealDB endpoint URL (default: http://localhost:8000)
    SURREAL_NAMESPACE: Database namespace (default: docs)
    SURREAL_DATABASE: Database name (default: docs)
    SURREAL_USER: Username for authentication
    SURREAL_PASS: Password for authentication

Schema:
    The client will create three tables:
    - guides: Course/guide metadata
    - sections: Individual documentation pages
    - chunks: Searchable text chunks with embeddings

Vector Search:
    Chunks table includes a vector index for semantic search using cosine similarity.
"""

import os
import logging
from typing import Sequence

from surrealdb import AsyncSurreal, RecordID

from models import Guide, Section, Chunk


logger = logging.getLogger(__name__)


def get_connection_config() -> dict:
    """
    Get SurrealDB connection configuration from environment.

    Returns:
        Dictionary with connection parameters
    """
    return {
        "url": os.getenv("SURREAL_URL", "http://localhost:8000"),
        "namespace": os.getenv("SURREAL_NAMESPACE", "docs"),
        "database": os.getenv("SURREAL_DATABASE", "docs"),
        "username": os.getenv("SURREAL_USER", "root"),
        "password": os.getenv("SURREAL_PASS", "root"),
    }


class DocsDatabase:
    """
    SurrealDB client for documentation storage.

    Usage:
        ```python
        async with DocsDatabase() as db:
            await db.init_schema()
            await db.upsert_guide(guide)
            await db.upsert_sections(sections)
            await db.upsert_chunks(chunks)
        ```
    """

    def __init__(self):
        self.config = get_connection_config()
        self.db = None

    async def __aenter__(self):
        """Initialize connection and authenticate."""
        logger.info(f"Connecting to SurrealDB at {self.config['url']}")

        # AsyncSurreal returns AsyncHttpSurrealConnection for http:// URLs
        self.db = AsyncSurreal(self.config["url"])

        # Enter the connection's context manager
        await self.db.__aenter__()

        # Authenticate - for remote instances, include namespace/database
        try:
            await self.db.signin({
                "username": self.config["username"],
                "password": self.config["password"],
                "namespace": self.config["namespace"],
                "database": self.config["database"],
            })
        except Exception as e:
            if "authentication" in str(e).lower():
                self._print_debug_curl()
            raise

        # Select namespace and database
        await self.db.use(self.config["namespace"], self.config["database"])

        logger.info("Connected to SurrealDB")
        return self

    def _print_debug_curl(self):
        """Print curl command for debugging authentication issues."""
        curl_cmd = f'''
Authentication failed. Test with curl:

# Root auth (local):
curl -X POST {self.config["url"]}/rpc \\
  -H "Content-Type: application/json" \\
  -d '{{"id":1,"method":"signin","params":[{{"user":"{self.config["username"]}","pass":"***"}}]}}'

# Namespace auth (remote/cloud):
curl -X POST {self.config["url"]}/rpc \\
  -H "Content-Type: application/json" \\
  -d '{{"id":1,"method":"signin","params":[{{"ns":"{self.config["namespace"]}","db":"{self.config["database"]}","user":"{self.config["username"]}","pass":"***"}}]}}'

Your .env config:
  SURREAL_URL={self.config["url"]}
  SURREAL_NAMESPACE={self.config["namespace"]}
  SURREAL_DATABASE={self.config["database"]}
  SURREAL_USER={self.config["username"]}
  SURREAL_PASS=***
'''
        print(curl_cmd)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close connection."""
        if self.db:
            await self.db.__aexit__(exc_type, exc_val, exc_tb)
        logger.info("Disconnected from SurrealDB")

    async def init_schema(self):
        """
        Initialize database schema.

        Creates tables and indexes for guides, sections, and chunks.
        Safe to run multiple times (uses OVERWRITE for definitions).
        """
        logger.info("Initializing database schema")

        # Define guides table
        await self.db.query("""
            DEFINE TABLE guides SCHEMAFULL;
            DEFINE FIELD slug ON guides TYPE string;
            DEFINE FIELD title ON guides TYPE string;
            DEFINE FIELD category ON guides TYPE string;
            DEFINE FIELD lang ON guides TYPE string;
            DEFINE FIELD order ON guides TYPE int;
            DEFINE FIELD updated_at ON guides TYPE datetime;
            DEFINE INDEX idx_guides_lang ON guides FIELDS lang;
            DEFINE INDEX idx_guides_category ON guides FIELDS category;
        """)

        # Define sections table
        await self.db.query("""
            DEFINE TABLE sections SCHEMAFULL;
            DEFINE FIELD slug ON sections TYPE string;
            DEFINE FIELD guide_id ON sections TYPE string;
            DEFINE FIELD title ON sections TYPE string;
            DEFINE FIELD url ON sections TYPE string;
            DEFINE FIELD content ON sections TYPE string;
            DEFINE FIELD content_hash ON sections TYPE string;
            DEFINE FIELD lang ON sections TYPE string;
            DEFINE FIELD order ON sections TYPE int;
            DEFINE FIELD updated_at ON sections TYPE datetime;
            DEFINE INDEX idx_sections_guide ON sections FIELDS guide_id;
            DEFINE INDEX idx_sections_lang ON sections FIELDS lang;
            DEFINE INDEX idx_sections_url ON sections FIELDS url UNIQUE;
        """)

        # Define chunks table with vector index
        await self.db.query("""
            DEFINE TABLE chunks SCHEMAFULL;
            DEFINE FIELD section_id ON chunks TYPE string;
            DEFINE FIELD guide_id ON chunks TYPE string;
            DEFINE FIELD heading ON chunks TYPE option<string>;
            DEFINE FIELD content ON chunks TYPE string;
            DEFINE FIELD chunk_index ON chunks TYPE int;
            DEFINE FIELD lang ON chunks TYPE string;
            DEFINE FIELD embedding ON chunks TYPE array<float>;
            DEFINE INDEX idx_chunks_section ON chunks FIELDS section_id;
            DEFINE INDEX idx_chunks_guide ON chunks FIELDS guide_id;
            DEFINE INDEX idx_chunks_lang ON chunks FIELDS lang;
            DEFINE INDEX idx_chunks_embedding ON chunks FIELDS embedding MTREE DIMENSION 1536 DIST COSINE;
        """)

        logger.info("Schema initialized")

    async def clear_data(self, lang: str = "ru"):
        """
        Clear all data for a specific language.

        Args:
            lang: Language code to clear
        """
        logger.warning(f"Clearing all data for lang={lang}")

        await self.db.query(f"DELETE chunks WHERE lang = '{lang}'")
        await self.db.query(f"DELETE sections WHERE lang = '{lang}'")
        await self.db.query(f"DELETE guides WHERE lang = '{lang}'")

        logger.info("Data cleared")

    async def clear_all_data(self):
        """
        Clear ALL data from all tables (use to clean up garbage).
        """
        logger.warning("Clearing ALL data from all tables")

        await self.db.query("DELETE chunks")
        await self.db.query("DELETE sections")
        await self.db.query("DELETE guides")

        logger.info("All data cleared")

    async def purge_database(self):
        """
        Remove ALL tables including garbage tables with wrong names.
        Use this to completely reset the database.
        """
        logger.warning("PURGING entire database - removing all tables")

        # Get list of all tables
        result = await self.db.query("INFO FOR DB")
        if result and isinstance(result, dict) and "tables" in result:
            tables = result["tables"]
            for table_name in tables.keys():
                logger.info(f"  Removing table: {table_name}")
                await self.db.query(f"REMOVE TABLE `{table_name}`")

        logger.info("Database purged")

    async def upsert_guide(self, guide: Guide):
        """
        Insert or update a guide.

        Args:
            guide: Guide to upsert
        """
        data = guide.to_dict()
        record_id = data.pop("id")

        # Use RecordID for proper escaping
        table, rid = record_id.split(":", 1)
        logger.debug(f"Upserting guide: {record_id} -> {data}")
        result = await self.db.upsert(RecordID(table, rid), data)
        logger.debug(f"Upsert guide result: {result}")

    async def upsert_section(self, section: Section):
        """
        Insert or update a single section.

        Args:
            section: Section to upsert
        """
        data = section.to_dict()
        record_id = data.pop("id")

        # Use RecordID for proper escaping
        table, rid = record_id.split(":", 1)
        logger.debug(f"Upserting section: {record_id}")
        result = await self.db.upsert(RecordID(table, rid), data)
        logger.debug(f"Upsert section result: {result}")

    async def upsert_sections(self, sections: Sequence[Section]):
        """
        Insert or update multiple sections.

        Args:
            sections: Sections to upsert
        """
        for section in sections:
            await self.upsert_section(section)

        logger.debug(f"Upserted {len(sections)} sections")

    async def upsert_chunks(self, chunks: Sequence[Chunk]):
        """
        Insert or update multiple chunks.

        Args:
            chunks: Chunks to upsert
        """
        for chunk in chunks:
            await self.upsert_chunk(chunk)

        logger.debug(f"Upserted {len(chunks)} chunks")

    async def upsert_chunk(self, chunk: Chunk):
        """
        Insert or update a single chunk.

        Args:
            chunk: Chunk to upsert
        """
        data = chunk.to_dict()
        record_id = data.pop("id")

        # Use RecordID for proper escaping
        table, rid = record_id.split(":", 1)
        result = await self.db.upsert(RecordID(table, rid), data)
        logger.debug(f"Upsert chunk {record_id}: {type(result)}")

    async def get_stats(self) -> dict:
        """
        Get database statistics.

        Returns:
            Dictionary with counts for each table
        """
        # query() returns result directly (not wrapped in array)
        result = await self.db.query("""
            RETURN {
                guides: (SELECT count() FROM guides GROUP ALL).count,
                sections: (SELECT count() FROM sections GROUP ALL).count,
                chunks: (SELECT count() FROM chunks GROUP ALL).count
            }
        """)

        return result if isinstance(result, dict) else {}

    async def get_existing_guides(self, lang: str) -> set[str]:
        """
        Get all existing guide IDs for a language.

        Used to detect orphaned guides (deleted from source).

        Args:
            lang: Language code (e.g., "ru")

        Returns:
            Set of guide IDs (e.g., {"guides:ru_course-name", ...})
        """
        result = await self.db.query(
            "SELECT id FROM guides WHERE lang = $lang",
            {"lang": lang}
        )

        if not result or not isinstance(result, list):
            return set()

        guide_ids = set()
        for row in result:
            raw_id = row.get("id", "")
            row_id = self._normalize_record_id(str(raw_id))
            if row_id:
                guide_ids.add(row_id)

        logger.debug(f"Found {len(guide_ids)} existing guides for lang={lang}")
        return guide_ids

    async def delete_guide(self, guide_id: str):
        """
        Delete a guide and all its sections and chunks.

        Used when a guide is removed from the source documentation.
        Deletes in batches to avoid timeouts on large datasets.

        Args:
            guide_id: Guide identifier (e.g., "guides:ru_course-name")
        """
        import time

        # First, count how many chunks/sections we need to delete
        count_result = await self.db.query(
            "SELECT count() as cnt FROM chunks WHERE guide_id = $guide_id GROUP ALL",
            {"guide_id": guide_id}
        )
        chunk_count = count_result[0].get("cnt", 0) if count_result else 0
        logger.info(f"    Guide has {chunk_count} chunks to delete")

        count_result = await self.db.query(
            "SELECT count() as cnt FROM sections WHERE guide_id = $guide_id GROUP ALL",
            {"guide_id": guide_id}
        )
        section_count = count_result[0].get("cnt", 0) if count_result else 0
        logger.info(f"    Guide has {section_count} sections to delete")

        # Delete chunks in batches
        batch_size = 50
        total_chunks_deleted = 0

        while True:
            t0 = time.time()
            ids_result = await self.db.query(
                f"SELECT id FROM chunks WHERE guide_id = $guide_id LIMIT {batch_size}",
                {"guide_id": guide_id}
            )
            t1 = time.time()

            if not ids_result or not isinstance(ids_result, list) or len(ids_result) == 0:
                break

            logger.info(f"    SELECT took {t1-t0:.2f}s, got {len(ids_result)} ids")

            # Delete each chunk by ID
            t2 = time.time()
            for row in ids_result:
                chunk_id = self._normalize_record_id(str(row.get("id", "")))
                if chunk_id:
                    table, rid = chunk_id.split(":", 1)
                    await self.db.delete(RecordID(table, rid))
                    total_chunks_deleted += 1
            t3 = time.time()

            logger.info(f"    DELETE batch took {t3-t2:.2f}s, total deleted: {total_chunks_deleted}/{chunk_count}")

        # Delete sections in batches
        total_sections_deleted = 0
        while True:
            ids_result = await self.db.query(
                f"SELECT id FROM sections WHERE guide_id = $guide_id LIMIT {batch_size}",
                {"guide_id": guide_id}
            )

            if not ids_result or not isinstance(ids_result, list) or len(ids_result) == 0:
                break

            for row in ids_result:
                section_id = self._normalize_record_id(str(row.get("id", "")))
                if section_id:
                    table, rid = section_id.split(":", 1)
                    await self.db.delete(RecordID(table, rid))
                    total_sections_deleted += 1

            logger.info(f"    Sections deleted: {total_sections_deleted}/{section_count}")

        # Delete the guide itself
        table, rid = guide_id.split(":", 1)
        await self.db.delete(RecordID(table, rid))

        logger.info(f"Deleted orphaned guide: {guide_id} ({total_sections_deleted} sections, {total_chunks_deleted} chunks)")

    async def get_existing_sections(self, guide_id: str) -> dict[str, str]:
        """
        Get all existing sections for a guide with their content hashes.

        Used for incremental updates:
        - Compare hashes to detect changed content
        - Detect orphaned sections (deleted from source)

        Args:
            guide_id: Guide identifier (e.g., "guides:ru_systems-thinking")

        Returns:
            Dictionary mapping section_id to content_hash
        """
        result = await self.db.query(
            "SELECT id, content_hash FROM sections WHERE guide_id = $guide_id",
            {"guide_id": guide_id}
        )

        if not result or not isinstance(result, list):
            return {}

        # result is list of rows - extract id as string
        hashes = {}
        for row in result:
            # id might be RecordID object, convert to string
            row_id = str(row.get("id", ""))
            # Normalize ID: remove SurrealDB escaping brackets ⟨...⟩
            row_id = self._normalize_record_id(row_id)
            content_hash = row.get("content_hash", "")
            if row_id:
                hashes[row_id] = content_hash

        logger.debug(f"Found {len(hashes)} existing sections for {guide_id}")
        return hashes

    def _normalize_record_id(self, record_id: str) -> str:
        """
        Normalize SurrealDB record ID by removing escape brackets.

        SurrealDB returns IDs like: sections:⟨ru_guide_page⟩
        We need: sections:ru_guide_page
        """
        # Remove ⟨ and ⟩ brackets used by SurrealDB for escaping
        return record_id.replace("⟨", "").replace("⟩", "")

    async def delete_section_chunks(self, section_id: str):
        """
        Delete all chunks for a specific section.

        Called before re-inserting chunks for a changed section.

        Args:
            section_id: Section identifier
        """
        await self.db.query(
            "DELETE chunks WHERE section_id = $section_id",
            {"section_id": section_id}
        )
        logger.debug(f"Deleted chunks for section: {section_id}")

    async def delete_section(self, section_id: str):
        """
        Delete a section and all its chunks.

        Used when a section is removed from the source documentation.

        Args:
            section_id: Section identifier (e.g., "sections:ru_guide_page")
        """
        # First delete all chunks
        await self.delete_section_chunks(section_id)

        # Then delete the section itself
        table, rid = section_id.split(":", 1)
        await self.db.delete(RecordID(table, rid))
        logger.info(f"Deleted orphaned section: {section_id}")


# MCP Query Methods (for reference - to be used in MCP server)

async def get_guides_list(db: AsyncSurreal, lang: str = "ru") -> list[dict]:
    """
    Get list of all guides.

    MCP Method: get_guides_list()

    Args:
        db: SurrealDB connection
        lang: Language filter

    Returns:
        List of guide dictionaries
    """
    # query() returns list of rows directly for SELECT
    result = await db.query(
        "SELECT id, slug, title, category, order FROM guides "
        "WHERE lang = $lang ORDER BY category, order",
        {"lang": lang}
    )
    return result if isinstance(result, list) else []


async def get_guide_sections(db: AsyncSurreal, guide_id: str) -> list[dict]:
    """
    Get all sections for a guide.

    MCP Method: get_guide_sections(guide_id)

    Args:
        db: SurrealDB connection
        guide_id: Guide identifier (e.g., "guide:ru_systems-thinking-introduction")

    Returns:
        List of section dictionaries (without content for efficiency)
    """
    result = await db.query(
        "SELECT id, slug, title, url, order FROM sections "
        "WHERE guide_id = $guide_id ORDER BY order",
        {"guide_id": guide_id}
    )
    return result if isinstance(result, list) else []


async def get_section_content(db: AsyncSurreal, section_url: str) -> dict | None:
    """
    Get full content of a section by URL.

    MCP Method: get_section_content(section_url)

    Args:
        db: SurrealDB connection
        section_url: Full URL path (e.g., "/ru/personal/systems-thinking/page")

    Returns:
        Section dictionary with full content, or None if not found
    """
    result = await db.query(
        "SELECT * FROM sections WHERE url = $url LIMIT 1",
        {"url": section_url}
    )
    # result is list of rows, return first or None
    return result[0] if result else None


async def find_chunks_by_text(
    db: AsyncSurreal,
    query_embedding: list[float],
    lang: str = "ru",
    limit: int = 10
) -> list[dict]:
    """
    Find chunks by semantic similarity.

    MCP Method: find_chunks_by_text(text)

    Note: The actual text-to-embedding conversion should happen before calling this.
    Use embeddings.generate_query_embedding() to convert text to embedding.

    Args:
        db: SurrealDB connection
        query_embedding: Vector embedding of search query
        lang: Language filter
        limit: Maximum results to return

    Returns:
        List of chunk dictionaries with similarity scores
    """
    result = await db.query(
        """
        SELECT
            id,
            section_id,
            guide_id,
            heading,
            content,
            vector::similarity::cosine(embedding, $embedding) AS score
        FROM chunks
        WHERE lang = $lang
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"embedding": query_embedding, "lang": lang, "limit": limit}
    )
    return result if isinstance(result, list) else []
