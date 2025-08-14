# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a VitePress-based documentation site for systems thinking and methodology courses. The repository contains educational content in both Russian and English, organized by course topics like systems thinking, rational work, intellect stack, and systems engineering.

## Development Commands

### VitePress Development
```bash
cd docs
npm run docs:dev      # Start development server
npm run docs:build    # Build for production
npm run docs:preview  # Preview production build
```

### Content Import and Translation Scripts
```bash
# Import course content from API
cd scripts/import_md
./run.sh [course_name]  # Imports all courses from metadata repo, or specific course if provided

# Translate content from Russian to English  
cd scripts/translate_md
./run.sh [force]  # Translates systems-thinking courses, 'force' to overwrite existing
```

## Project Structure

### Content Organization
- `docs/` - VitePress documentation root
  - `en/` - English content (translated)
  - `ru/` - Russian content (source)
  - `public/` - Static assets (images)
  - `index.md` - Root index page

### Course Structure
Content is organized by course topics:
- `systems-thinking-introduction/` - Introduction to systems thinking
- `rational-work/` - Rational work methodology
- `intellect-stack/` - Intellect development
- `methodology/` - General methodology
- `systems-engineering/` - Systems engineering
- `systems-management/` - Systems management

Each course contains:
- `index.md` - Course overview
- Sectioned content with modeling exercises
- Associated images in `public/` directories

### Scripts Architecture
- `scripts/import_md/` - Import course content from API using external metadata repo
- `scripts/translate_md/` - Translate Russian content to English
- `scripts/header/` - Header processing utilities
- `scripts/import_docs/` - Legacy import scripts (structured data)

## Content Management

### Import Workflow
1. Run `scripts/import_md/run.sh` to import course content
2. Script clones external metadata repository for course definitions
3. Content is imported as Russian markdown files in `docs/ru/`
4. Images are downloaded and stored in `docs/public/ru/`
5. Old versions are cleaned up before import

### Translation Workflow
1. Run `scripts/translate_md/run.sh` to translate Russian content to English
2. Currently focused on systems-thinking courses only
3. Translated content is generated in `docs/en/`
4. Creates backup before translation, removes backup on success
5. Uses OpenAI API for translation with LangChain integration

### Image Assets
- Course images stored in `docs/public/[lang]/[course]/`
- Images are numbered sequentially (0.png, 1.jpeg, etc.)
- Import script handles image downloading and local path conversion

## Dependencies

### Node.js Dependencies
- VitePress for static site generation
- gray-matter for frontmatter parsing
- markdown-it-footnote for footnote support

### Python Dependencies
- requests for API calls
- markdownify for HTML to Markdown conversion
- python-slugify for URL-friendly slugs
- OpenAI and LangChain for translation services
- langsmith for translation tracking

## Environment Variables

- `AISYSTANT_SESSION_TOKEN` - Required for content import scripts
- `LOG_LEVEL` - Controls logging verbosity (default: INFO)
- OpenAI API credentials for translation services

## External Dependencies

- GitHub repository: `github.com/aisystant/metadata` - Contains course metadata YAML files used for import process