# Publish to SurrealDB

This script publishes the VitePress documentation to SurrealDB for use with the MCP server.

## Incremental Updates

**By default, only changed content is processed.** This saves significant time and API costs.

How it works:
1. Each section stores a `content_hash` (SHA-256 of markdown content)
2. On update, new hashes are compared with existing ones in DB
3. Only sections with changed hashes get new embeddings generated
4. Unchanged sections are skipped entirely
5. **Orphan cleanup**: Sections deleted from source docs are automatically removed from DB

```
First run:     500 sections → 500 embeddings generated ($$)
Second run:    500 sections → 0 embeddings (no changes)
After edit:    500 sections → 3 embeddings (only changed files)
Delete file:   499 sections → 1 section deleted from DB
```

Use `--force` to regenerate all embeddings regardless of changes.

## Interruptible Processing

**You can interrupt the script at any time (Ctrl+C) and resume later.**

Each section is saved individually, so:
- Interrupted sections will be reprocessed on next run
- Completed sections keep their embeddings
- No embedding costs are wasted

```
Run 1:  Started processing 500 sections... Ctrl+C at section 200
Run 2:  Continues from section 201 (sections 1-200 already done)
```

## Data Model

```
┌─────────────────────────────────────────────────────────────────┐
│                          GUIDES                                  │
├─────────────────────────────────────────────────────────────────┤
│ id: guide:ru_systems-thinking-introduction                      │
│ slug: "systems-thinking-introduction"                           │
│ title: "Введение в системное мышление"                          │
│ category: "personal" | "professional" | "research"              │
│ lang: "ru"                                                      │
│ order: 1                                                        │
│ updated_at: datetime                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SECTIONS                                 │
├─────────────────────────────────────────────────────────────────┤
│ id: section:ru_systems-thinking-introduction_word-object-system │
│ guide_id: "guide:ru_systems-thinking-introduction"              │
│ slug: "word-object-system"                                      │
│ title: "Слово, объект, система"                                 │
│ url: "/ru/personal/systems-thinking-introduction/..."           │
│ content: "# Full markdown content..."                           │
│ content_hash: "a1b2c3d4e5f6..."  ← for incremental updates      │
│ lang: "ru"                                                      │
│ order: 5                                                        │
│ updated_at: datetime                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          CHUNKS                                  │
├─────────────────────────────────────────────────────────────────┤
│ id: chunk:ru_systems-thinking-introduction_word-object-system_0 │
│ section_id: "section:..."                                       │
│ guide_id: "guide:..."                                           │
│ heading: "Parent heading"                                       │
│ content: "Text chunk for search..."                             │
│ chunk_index: 0                                                  │
│ lang: "ru"                                                      │
│ embedding: vector<1536>                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Language Support

**Current**: Only Russian (`ru`) content is processed.

All database records include a `lang` field to support future multi-language content. To add English support:

1. Ensure `docs/en/` directory has content with the same structure as `docs/ru/`
2. Modify `LANGUAGES` constant in `main.py`:
   ```python
   LANGUAGES = ["ru", "en"]
   ```
3. Re-run the publish script

## Chunking Strategy

Content is split into searchable chunks using this strategy:

1. **Split by headings** (h1-h6) to maintain semantic structure
2. **Split large chunks by sentences** if content exceeds 1000 characters
3. **Sliding window** with 2-sentence overlap for context preservation

```
Markdown Content
       │
       ▼
┌──────────────────┐
│ Split by Headings │
└────────┬─────────┘
         │
         ▼
    len > 1000?
    /        \
   No        Yes
   │          │
   ▼          ▼
 Keep    Split by sentences
 as-is   (sliding window)
```

## MCP Methods

The data model supports these MCP server methods:

| Method | Description | SurrealDB Query |
|--------|-------------|-----------------|
| `get_guides_list()` | List all guides | `SELECT * FROM guides WHERE lang = $lang ORDER BY category, order` |
| `get_guide_sections(guide_id)` | Get sections for a guide | `SELECT * FROM sections WHERE guide_id = $id ORDER BY order` |
| `get_section_content(section_url)` | Get full section content | `SELECT * FROM sections WHERE url = $url` |
| `find_chunks_by_text(text, lang?)` | Semantic search | Vector similarity search on `chunks.embedding` with `lang` filter |

## Usage

### Prerequisites

1. Running SurrealDB instance
2. OpenAI API key for embeddings

### Environment Variables

```bash
# Required
export OPENAI_API_KEY=sk-...

# Optional (defaults shown)
export SURREAL_URL=http://localhost:8000
export SURREAL_NAMESPACE=docs
export SURREAL_DATABASE=docs
export SURREAL_USER=root
export SURREAL_PASS=root
export LOG_LEVEL=INFO
```

### Running

```bash
# Normal publish (incremental - only changed sections)
./run.sh

# Force regenerate all embeddings
./run.sh --force

# Clear all data and republish from scratch
./run.sh --clear

# Dry run (parse only, don't write to database)
./run.sh --dry-run

# Skip embedding generation (for testing)
./run.sh --skip-embeddings
```

### Example Output

First run (all new):
```
[INFO] Processing: Введение в системное мышление
[INFO]   120 changed, 0 unchanged
[INFO]   Generating embeddings for 450 chunks...
[INFO]   Published: 120 updated, 450 chunks
```

Subsequent run (no changes):
```
[INFO] Processing: Введение в системное мышление
[INFO]   No changes detected, skipping embeddings
[INFO]   Published: 0 updated, 0 chunks
```

After editing 2 files:
```
[INFO] Processing: Введение в системное мышление
[INFO]   2 changed, 118 unchanged
[INFO]   Generating embeddings for 8 chunks...
[INFO]   Published: 2 updated, 8 chunks
```

Final statistics:
```
==================================================
Publishing complete!
Session statistics:
  Guides processed: 13
  Sections total: 500
  Sections changed: 2
  Sections unchanged: 498
  Sections deleted: 0
  Chunks created: 8
  Embeddings generated: 8
Database totals:
  Guides: 13
  Sections: 500
  Chunks: 3200
```

## File Structure

```
scripts/publish_to_surreal/
├── README.md           # This file
├── run.sh              # Entry point script
├── main.py             # Main orchestration
├── models.py           # Data models (Guide, Section, Chunk)
├── parser.py           # Markdown parsing
├── chunker.py          # Text chunking logic
├── embeddings.py       # OpenAI embeddings
├── surreal_client.py   # SurrealDB operations
└── requirements.txt    # Python dependencies
```

## Starting SurrealDB

For local development:

```bash
# Using Docker
docker run --rm -p 8000:8000 surrealdb/surrealdb:latest start \
  --user root --pass root memory

# Or with file storage
docker run --rm -p 8000:8000 -v ./data:/data surrealdb/surrealdb:latest start \
  --user root --pass root file:/data/docs.db
```

## Query Examples

After publishing, you can query the data directly:

```sql
-- Get all guides
SELECT * FROM guides WHERE lang = 'ru' ORDER BY category, order;

-- Get sections for a guide
SELECT id, slug, title, url, order
FROM sections
WHERE guide_id = 'guide:ru_systems-thinking-introduction'
ORDER BY order;

-- Get section content by URL
SELECT * FROM sections
WHERE url = '/ru/personal/systems-thinking-introduction/word-object-system';

-- Semantic search (requires embedding vector)
SELECT
    id, section_id, heading, content,
    vector::similarity::cosine(embedding, $query_embedding) AS score
FROM chunks
WHERE lang = 'ru'
ORDER BY score DESC
LIMIT 10;
```
