#!/usr/bin/env python3
"""
Publish documentation to SurrealDB.

This script parses the VitePress documentation, generates embeddings for
semantic search, and publishes everything to SurrealDB.

Incremental Updates:
    By default, only changed sections are processed. Content hashes are used
    to detect changes. Embeddings are only regenerated for modified content.
    Use --force to regenerate all embeddings.

Language Support:
    Currently only Russian (ru) content is processed.
    All database records include a `lang` field for future multi-language support.
    To add English support, modify LANGUAGES constant and ensure docs/en/ exists.

Usage:
    python main.py [--clear] [--force] [--skip-embeddings] [--dry-run]

Options:
    --clear             Clear existing data before publishing
    --force             Force regenerate all embeddings (ignore hashes)
    --skip-embeddings   Skip embedding generation (for testing)
    --dry-run           Parse docs but don't publish to database

Environment Variables:
    SURREAL_URL         SurrealDB endpoint (default: http://localhost:8000)
    SURREAL_NAMESPACE   Database namespace (default: docs)
    SURREAL_DATABASE    Database name (default: docs)
    SURREAL_USER        Username (default: root)
    SURREAL_PASS        Password (default: root)
    OPENAI_API_KEY      Required for embedding generation
    LOG_LEVEL           Logging verbosity (default: INFO)
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from parser import parse_docs, create_chunks
from embeddings import generate_single_embedding
from surreal_client import DocsDatabase


# Load .env file from script directory
load_dotenv(Path(__file__).parent / ".env")


# Currently only Russian is processed
# To add English: LANGUAGES = ["ru", "en"]
LANGUAGES = ["ru"]

# Path to docs directory (relative to this script)
DOCS_ROOT = Path(__file__).parent.parent.parent / "docs"


def setup_logging():
    """Configure logging based on LOG_LEVEL environment variable."""
    import os
    level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Publish documentation to SurrealDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before publishing"
    )

    parser.add_argument(
        "--purge",
        action="store_true",
        help="DANGEROUS: Remove ALL tables (including garbage) and recreate schema"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regenerate all embeddings (ignore content hashes)"
    )

    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Skip embedding generation (for testing)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse docs but don't publish to database"
    )

    parser.add_argument(
        "--docs-root",
        type=Path,
        default=DOCS_ROOT,
        help=f"Path to docs directory (default: {DOCS_ROOT})"
    )

    return parser.parse_args()


async def publish_docs(args):
    """
    Main publishing workflow.

    Interruptible Processing:
        Each section is processed and saved individually.
        You can interrupt (Ctrl+C) at any time and resume later.
        Only changed sections will be reprocessed on the next run.

    Incremental Update Strategy:
        1. Collect all guides from files
        2. Compare with existing guides in DB, delete orphaned guides
        3. For each guide, fetch existing sections from DB
        4. Compare content hashes to detect changes
        5. Delete orphaned sections (removed from source docs)
        6. Skip unchanged sections (no embedding cost)
        7. Process changed sections one by one

    Flow:
        1. Connect to SurrealDB
        2. Initialize schema
        3. Delete orphaned guides (in DB but not in files)
        4. For each guide:
            a. Upsert guide
            b. Delete orphaned sections (in DB but not in files)
            c. For each section from files:
                - Skip if hash unchanged
                - Upsert section
                - Delete old chunks
                - For each chunk: generate embedding → write to DB
        5. Print statistics
    """
    logger = logging.getLogger(__name__)

    if args.dry_run:
        logger.info("DRY RUN MODE - No data will be written to database")

    if args.force:
        logger.info("FORCE MODE - All embeddings will be regenerated")

    # Validate docs root
    if not args.docs_root.exists():
        logger.error(f"Docs directory not found: {args.docs_root}")
        sys.exit(1)

    # Statistics
    stats = {
        "guides_new": 0,
        "guides_updated": 0,
        "guides_deleted": 0,
        "sections_new": 0,
        "sections_changed": 0,
        "sections_unchanged": 0,
        "sections_deleted": 0,
        "chunks": 0,
        "embeddings_generated": 0,
    }

    # Connect to database (needed for both dry-run and real run to compare)
    async with DocsDatabase() as db:
        # Purge all tables if requested (DANGEROUS)
        if args.purge and not args.dry_run:
            await db.purge_database()

        # Initialize schema
        if not args.dry_run:
            await db.init_schema()

        # Clear data if requested
        if args.clear and not args.dry_run:
            for lang in LANGUAGES:
                await db.clear_data(lang)

        # Process each language
        for lang in LANGUAGES:
            logger.info(f"Processing language: {lang}")

            # First pass: collect all guides from files
            parsed_guides = {}  # guide_id -> (guide, sections)
            for guide, sections, _ in parse_docs(args.docs_root, lang=lang):
                parsed_guides[guide.id] = (guide, sections)

            logger.info(f"  Found {len(parsed_guides)} guides in files")

            # Get existing guides from DB
            existing_guide_ids = set()
            if not args.clear:
                existing_guide_ids = await db.get_existing_guides(lang)
            logger.info(f"  Found {len(existing_guide_ids)} guides in database")

            # Find and delete orphaned guides (in DB but not in files)
            orphaned_guide_ids = existing_guide_ids - set(parsed_guides.keys())
            if orphaned_guide_ids:
                logger.info(f"  Orphaned guides to delete: {len(orphaned_guide_ids)}")
                for orphan_guide_id in orphaned_guide_ids:
                    logger.info(f"    - {orphan_guide_id}")
                    if not args.dry_run:
                        await db.delete_guide(orphan_guide_id)
                    stats["guides_deleted"] += 1

            # Identify new guides
            new_guide_ids = set(parsed_guides.keys()) - existing_guide_ids

            # Process each guide
            for guide_id, (guide, sections) in parsed_guides.items():
                is_new_guide = guide_id in new_guide_ids

                if is_new_guide:
                    stats["guides_new"] += 1
                    logger.info(f"  [NEW] {guide.title}")
                else:
                    stats["guides_updated"] += 1
                    logger.info(f"  Processing: {guide.title}")

                # Upsert guide
                if not args.dry_run:
                    await db.upsert_guide(guide)

                # Get existing sections from DB (empty if --clear or new guide)
                existing_sections = {}
                if not args.clear and not is_new_guide:
                    existing_sections = await db.get_existing_sections(guide.id)

                # Build set of current section IDs (from parsed files)
                current_section_ids = {section.id for section in sections}

                # Find orphaned sections (in DB but not in files) and delete them
                orphaned_section_ids = set(existing_sections.keys()) - current_section_ids
                if orphaned_section_ids:
                    logger.info(f"    Orphaned sections: {len(orphaned_section_ids)}")
                    for orphan_id in orphaned_section_ids:
                        if not args.dry_run:
                            await db.delete_section(orphan_id)
                        stats["sections_deleted"] += 1

                # Process each section individually
                total_chunks = 0
                for section in sections:
                    old_hash = existing_sections.get(section.id, "")
                    is_new_section = section.id not in existing_sections

                    # Skip unchanged sections (unless --force)
                    if not args.force and old_hash == section.content_hash:
                        stats["sections_unchanged"] += 1
                        continue

                    if is_new_section:
                        stats["sections_new"] += 1
                    else:
                        stats["sections_changed"] += 1

                    if args.dry_run:
                        # In dry-run, just count chunks
                        section_chunks = create_chunks(section)
                        total_chunks += len(section_chunks)
                        status = "[NEW]" if is_new_section else "[CHANGED]"
                        logger.info(f"    {status} {section.slug}: {len(section_chunks)} chunks")
                    else:
                        # 1. Upsert section
                        await db.upsert_section(section)

                        # 2. Delete old chunks for this section
                        await db.delete_section_chunks(section.id)

                        # 3. Create and process chunks one by one
                        section_chunks = create_chunks(section)

                        for chunk in section_chunks:
                            if not args.skip_embeddings:
                                # Generate embedding
                                chunk = generate_single_embedding(chunk)
                                stats["embeddings_generated"] += 1

                            # Write to DB immediately
                            await db.upsert_chunk(chunk)
                            total_chunks += 1

                        logger.info(f"    {section.slug}: {len(section_chunks)} chunks")

                stats["chunks"] += total_chunks

        # Print final statistics
        logger.info("=" * 50)
        if args.dry_run:
            logger.info("DRY RUN SUMMARY (no changes made):")
        else:
            logger.info("Publishing complete!")

        logger.info(f"Guides:")
        logger.info(f"  New: {stats['guides_new']}")
        logger.info(f"  Updated: {stats['guides_updated']}")
        logger.info(f"  Deleted: {stats['guides_deleted']}")
        logger.info(f"Sections:")
        logger.info(f"  New: {stats['sections_new']}")
        logger.info(f"  Changed: {stats['sections_changed']}")
        logger.info(f"  Unchanged: {stats['sections_unchanged']}")
        logger.info(f"  Deleted: {stats['sections_deleted']}")
        logger.info(f"Chunks to process: {stats['chunks']}")
        if not args.dry_run:
            logger.info(f"Embeddings generated: {stats['embeddings_generated']}")

        # Show database totals
        if not args.dry_run:
            db_stats = await db.get_stats()
            logger.info(f"Database totals:")
            logger.info(f"  Guides: {db_stats.get('guides', 0)}")
            logger.info(f"  Sections: {db_stats.get('sections', 0)}")
            logger.info(f"  Chunks: {db_stats.get('chunks', 0)}")


def main():
    """Entry point."""
    setup_logging()
    args = parse_args()

    try:
        asyncio.run(publish_docs(args))
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.exception(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
