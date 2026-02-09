#!/usr/bin/env python3
"""
Fix grid tables in markdown files: convert Pandoc grid tables to pipe tables.

Pandoc outputs complex Word tables in "grid" format (+---+---+) which most
markdown renderers don't support. This script converts them to standard
pipe tables (| --- | --- |).

Usage:
    python3 fix_grid_tables.py <directory>   # Fix all .md files recursively
    python3 fix_grid_tables.py <file.md>     # Fix a single file
    python3 fix_grid_tables.py --dry-run <directory>  # Preview without changes
"""

import re
import os
import sys


def is_full_separator(line):
    """Check if line is a full grid table separator: +---+---+ or +===+===+"""
    return bool(re.match(r'^\+[-=+]+\+\s*$', line.strip()))


def is_header_separator(line):
    """Header separator uses = instead of -: +===+===+"""
    return is_full_separator(line) and '=' in line


def has_partial_separator(line):
    """Content line with embedded separators for row spans: |...+---+---+"""
    stripped = line.strip()
    if not stripped.startswith('|'):
        return False
    return bool(re.search(r'\+[-=]{2,}', stripped))


def get_col_positions(sep_line):
    """Get positions of + chars in a separator line."""
    return [i for i, ch in enumerate(sep_line.rstrip()) if ch == '+']


def extract_cell_text(line, start, end):
    """Extract cell text from a content line between column boundaries."""
    if start >= len(line):
        return ''
    actual_end = min(end, len(line))
    text = line[start:actual_end]
    text = text.strip()
    # Remove stray border pipes at edges
    if text.startswith('|'):
        text = text[1:]
    if text.endswith('|'):
        text = text[:-1]
    return text.strip()


def convert_grid_tables(text):
    """Replace all grid tables in text with pipe tables."""
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        if is_full_separator(lines[i]):
            # Collect the entire grid table block
            block = [lines[i]]
            i += 1
            while i < len(lines):
                stripped = lines[i].strip()
                if is_full_separator(lines[i]):
                    block.append(lines[i])
                    i += 1
                    # Table continues if next line is content
                    if i < len(lines) and lines[i].strip().startswith('|'):
                        continue
                    else:
                        break
                elif stripped.startswith('|'):
                    block.append(lines[i])
                    i += 1
                else:
                    break

            # Need at least 2 full separators for a valid table
            sep_count = sum(1 for l in block if is_full_separator(l))
            if sep_count >= 2:
                pipe_lines = _convert_block(block)
                result.extend(pipe_lines)
            else:
                result.extend(block)
        else:
            result.append(lines[i])
            i += 1

    return '\n'.join(result)


def _convert_block(block):
    """Convert one grid table block to pipe table lines."""
    # Find reference column positions from the separator with most columns
    all_seps = []
    for line in block:
        if is_full_separator(line):
            positions = get_col_positions(line)
            all_seps.append((line, positions))

    if not all_seps:
        return block

    ref_line, ref_pos = max(all_seps, key=lambda x: len(x[1]))
    num_cols = len(ref_pos) - 1

    if num_cols < 1:
        return block

    # Detect spanning regions: separators with fewer columns than reference
    # These introduce "spanning header" rows (e.g. table title spanning all columns)
    narrow_seps = set()
    for line, positions in all_seps:
        if len(positions) - 1 < num_cols:
            narrow_seps.add(line)

    # Parse rows
    rows = []
    cells = [[] for _ in range(num_cols)]
    header_row = None
    prefix_paragraphs = []
    in_spanning_region = False

    for line in block:
        if is_full_separator(line):
            # Flush current cells
            if any(cells[c] for c in range(num_cols)):
                if in_spanning_region:
                    # Spanning row → paragraph before the table
                    all_text = ' '.join(
                        ' '.join(cells[c]) for c in range(num_cols) if cells[c]
                    )
                    if all_text.strip():
                        prefix_paragraphs.append(all_text.strip())
                else:
                    row = [' '.join(c) for c in cells]
                    rows.append(row)

            cells = [[] for _ in range(num_cols)]

            # Check if this is a narrow (spanning) separator
            in_spanning_region = line in narrow_seps

            # Mark header
            if is_header_separator(line) and rows:
                header_row = len(rows) - 1

        elif has_partial_separator(line):
            # Partial separator = row break for some columns (row spans)
            if any(cells[c] for c in range(num_cols)):
                row = [' '.join(c) for c in cells]
                rows.append(row)
            cells = [[] for _ in range(num_cols)]

        elif line.strip().startswith('|'):
            # Content line — extract cell text at each column position
            for c in range(num_cols):
                start = ref_pos[c] + 1
                end = ref_pos[c + 1]
                text = extract_cell_text(line, start, end)
                if text:
                    cells[c].append(text)

    # Flush remaining
    if any(cells[c] for c in range(num_cols)):
        row = [' '.join(c) for c in cells]
        rows.append(row)

    if not rows:
        return block

    # Default header to first row
    if header_row is None:
        header_row = 0

    # Build output
    output = []

    for p in prefix_paragraphs:
        output.append('')
        output.append(p)
        output.append('')

    for r_idx, row in enumerate(rows):
        # Escape any pipe characters inside cell content
        escaped_row = [cell.replace('|', '\\|') for cell in row]
        output.append('| ' + ' | '.join(escaped_row) + ' |')
        if r_idx == header_row:
            output.append('|' + '|'.join(' --- ' for _ in range(num_cols)) + '|')

    return output


def fix_file(filepath, dry_run=False):
    """Fix grid tables in a single file. Returns True if changes were made."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    # Quick check: does this file contain grid tables?
    if not re.search(r'^\+[-=+]+\+\s*$', original, re.MULTILINE):
        return False

    fixed = convert_grid_tables(original)

    if fixed != original:
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed)
        return True
    return False


def fix_directory(dirpath, dry_run=False):
    """Fix grid tables in all .md files in directory (recursive)."""
    fixed_count = 0
    for root, dirs, files in os.walk(dirpath):
        for fname in sorted(files):
            if fname.endswith('.md'):
                fpath = os.path.join(root, fname)
                if fix_file(fpath, dry_run=dry_run):
                    label = "[DRY RUN] Would fix" if dry_run else "Fixed"
                    print(f"  {label}: {os.path.relpath(fpath, dirpath)}")
                    fixed_count += 1
    return fixed_count


def main():
    dry_run = '--dry-run' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--dry-run']

    if not args:
        print(__doc__)
        sys.exit(1)

    target = args[0]
    if os.path.isdir(target):
        count = fix_directory(target, dry_run=dry_run)
        label = "Would fix" if dry_run else "Fixed"
        print(f"\n{label} {count} file(s).")
    elif os.path.isfile(target):
        if fix_file(target, dry_run=dry_run):
            label = "[DRY RUN] Would fix" if dry_run else "Fixed"
            print(f"{label}: {target}")
        else:
            print("No grid tables found.")
    else:
        print(f"Not found: {target}")
        sys.exit(1)


if __name__ == '__main__':
    main()
