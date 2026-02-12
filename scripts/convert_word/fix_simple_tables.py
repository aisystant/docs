#!/usr/bin/env python3
"""
Fix Pandoc simple tables in markdown files: convert to pipe tables.

Pandoc simple tables use space-aligned columns with dashed separators:

  -------------------------------------------------------
  Header1        Header2              Header3
  -------------- -------------------- -------------------
  Cell1          Cell2                Cell3
  -------------------------------------------------------

This script converts them to standard pipe tables (| --- | --- |).

Usage:
    python3 fix_simple_tables.py <directory>   # Fix all .md files recursively
    python3 fix_simple_tables.py <file.md>     # Fix a single file
    python3 fix_simple_tables.py --dry-run <directory>  # Preview without changes
"""

import re
import os
import sys


def is_simple_table_separator(line):
    """Check if line is a simple table separator: groups of dashes separated by spaces.

    Examples:
      --------------------------------------------------------------------------------------
      -------- ---------------------------------------- ------------------------------------
      ----- ----------------------- ---------------------- -----
    """
    stripped = line.strip()
    if not stripped:
        return False
    # Must be only dashes and spaces, at least 10 chars of dashes total
    if not re.match(r'^[-\s]+$', stripped):
        return False
    dash_count = stripped.count('-')
    if dash_count < 10:
        return False
    # Must have at least one group of 3+ dashes
    if not re.search(r'-{3,}', stripped):
        return False
    # Should not be a YAML delimiter (exactly "---")
    if stripped == '---':
        return False
    # Should not be a horizontal rule (exactly "---" or "----" alone, no spaces)
    if re.match(r'^-+$', stripped) and dash_count <= 5:
        return False
    return True


def get_column_boundaries(sep_line):
    """Extract column start/end positions from a separator line with multiple dash groups.

    Returns list of (start, end) tuples for each column.
    """
    # Find all groups of dashes
    columns = []
    for m in re.finditer(r'-{2,}', sep_line):
        columns.append((m.start(), m.end()))
    return columns


def is_full_width_separator(sep_line, columns):
    """Check if separator is a single full-width dash line (no gaps = no column info)."""
    return len(columns) <= 1


def extract_cell_text(line, col_start, col_end, line_len):
    """Extract text from a line at given column positions."""
    if col_start >= line_len:
        return ''
    actual_end = min(col_end, line_len)
    return line[col_start:actual_end].strip()


def find_column_separator(block_lines, full_seps):
    """Find the column separator line (the one with gaps between dash groups).

    In a simple table:
    - Full-width separators (top/bottom) have one continuous dash group
    - Column separator has multiple dash groups showing column widths
    """
    for i, line in enumerate(block_lines):
        if i in full_seps:
            continue
        if is_simple_table_separator(line):
            cols = get_column_boundaries(line)
            if len(cols) >= 2:
                return i, cols
    return None, None


def parse_simple_table_block(block_lines):
    """Parse a simple table block into header and data rows.

    Returns (headers, rows) or None if not a valid table.
    """
    if len(block_lines) < 3:
        return None

    # Identify all separator lines
    sep_indices = set()
    for i, line in enumerate(block_lines):
        if is_simple_table_separator(line):
            sep_indices.add(i)

    # Find column separator (the one with multiple dash groups)
    col_sep_idx, columns = find_column_separator(block_lines, set())

    if columns is None:
        # Try: maybe all seps are full-width, and column boundaries come from text alignment
        # Look for the first separator with multiple groups
        for i in sorted(sep_indices):
            cols = get_column_boundaries(block_lines[i])
            if len(cols) >= 2:
                col_sep_idx = i
                columns = cols
                break

    if columns is None or len(columns) < 2:
        return None

    # Determine which lines are headers (between first sep and column sep)
    # and which are data (between column sep and last sep)
    sorted_seps = sorted(sep_indices)
    if len(sorted_seps) < 2:
        return None

    first_sep = sorted_seps[0]
    last_sep = sorted_seps[-1]

    # Find the column separator (with gaps) - it separates header from data
    # If col_sep_idx is the same as first_sep, headers are before it
    header_lines = []
    data_lines = []

    if col_sep_idx is not None and col_sep_idx != first_sep and col_sep_idx != last_sep:
        # Standard case: first_sep, header_lines, col_sep, data_lines, last_sep
        header_lines = [block_lines[i] for i in range(first_sep + 1, col_sep_idx)
                        if i not in sep_indices]
        data_lines = [block_lines[i] for i in range(col_sep_idx + 1, last_sep)
                      if i not in sep_indices]
    elif col_sep_idx == first_sep:
        # Column sep is the first line — no separate header
        # Check if there's a second separator for header boundary
        if len(sorted_seps) >= 3:
            second_sep = sorted_seps[1]
            header_lines = [block_lines[i] for i in range(first_sep + 1, second_sep)
                            if i not in sep_indices]
            data_lines = [block_lines[i] for i in range(second_sep + 1, last_sep)
                          if i not in sep_indices]
        else:
            # Just two seps with column info — all content between them
            data_lines = [block_lines[i] for i in range(first_sep + 1, last_sep)
                          if i not in sep_indices]
    else:
        # Fallback: treat first non-blank content line as header
        data_lines = [block_lines[i] for i in range(first_sep + 1, last_sep)
                      if i not in sep_indices]

    # Extract header cells
    headers = []
    if header_lines:
        # Merge multi-line headers
        merged = ['' for _ in columns]
        for line in header_lines:
            for c_idx, (cstart, cend) in enumerate(columns):
                cell = extract_cell_text(line, cstart, cend, len(line))
                if cell:
                    if merged[c_idx]:
                        merged[c_idx] += ' ' + cell
                    else:
                        merged[c_idx] = cell
        headers = merged

    # Extract data rows — group by non-empty lines separated by empty lines
    rows = []
    current_cells = ['' for _ in columns]
    has_content = False

    for line in data_lines:
        stripped = line.strip()
        if stripped == '':
            # Empty line = row boundary
            if has_content:
                rows.append(current_cells)
                current_cells = ['' for _ in columns]
                has_content = False
            continue

        # Extract cells from this line
        for c_idx, (cstart, cend) in enumerate(columns):
            cell = extract_cell_text(line, cstart, cend, len(line))
            if cell:
                if current_cells[c_idx]:
                    current_cells[c_idx] += ' ' + cell
                else:
                    current_cells[c_idx] = cell
                has_content = True

    # Flush last row
    if has_content:
        rows.append(current_cells)

    if not headers and not rows:
        return None

    # If no headers found, use first row as header
    if not headers and rows:
        headers = rows[0]
        rows = rows[1:]

    return headers, rows


def table_to_pipe(headers, rows):
    """Convert parsed table data to pipe table format."""
    num_cols = len(headers)
    lines = []

    # Escape pipes in content
    def esc(text):
        return text.replace('|', '\\|')

    # Header row
    lines.append('| ' + ' | '.join(esc(h) for h in headers) + ' |')
    # Separator
    lines.append('|' + '|'.join(' --- ' for _ in range(num_cols)) + '|')
    # Data rows
    for row in rows:
        # Pad row to num_cols if needed
        padded = row + [''] * (num_cols - len(row))
        lines.append('| ' + ' | '.join(esc(c) for c in padded[:num_cols]) + ' |')

    return lines


def convert_simple_tables(text):
    """Replace all Pandoc simple tables in text with pipe tables."""
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        if is_simple_table_separator(lines[i]):
            # Potential start of a simple table — collect the block
            block_start = i
            block = [lines[i]]
            i += 1

            # Collect lines until we hit the closing separator or non-table content
            sep_count = 1
            while i < len(lines):
                line = lines[i]
                if is_simple_table_separator(line):
                    block.append(line)
                    sep_count += 1
                    i += 1
                    # Determine if this separator has column gaps (= column separator)
                    # or is full-width (= top/bottom separator)
                    cols = get_column_boundaries(line)
                    is_column_sep = len(cols) >= 2
                    # After a column separator, continue to collect data + closing sep
                    if is_column_sep and sep_count == 2:
                        continue
                    # Check if this is the closing separator
                    if i < len(lines):
                        next_stripped = lines[i].strip()
                        if (next_stripped == '' or
                            (not next_stripped.startswith('-') and
                             not _looks_like_table_content(lines[i], block))):
                            break
                    else:
                        break
                elif line.strip() == '' and sep_count >= 2:
                    # Empty line after 2+ separators might end the table
                    # But empty lines between rows are normal
                    # Look ahead: if next non-empty line is a separator, continue
                    lookahead = i + 1
                    while lookahead < len(lines) and lines[lookahead].strip() == '':
                        lookahead += 1
                    if lookahead < len(lines) and is_simple_table_separator(lines[lookahead]):
                        block.append(line)
                        i += 1
                    elif lookahead < len(lines) and _looks_like_table_content(lines[lookahead], block):
                        block.append(line)
                        i += 1
                    else:
                        # End of table
                        break
                elif line.strip() == '':
                    block.append(line)
                    i += 1
                else:
                    # Content line — include only if it looks like table content
                    if _looks_like_table_content(line, block):
                        block.append(line)
                        i += 1
                    else:
                        # Non-table content (paragraph text) — stop collecting
                        break

            # Need at least 2 separators for a valid simple table
            actual_seps = sum(1 for l in block if is_simple_table_separator(l))
            if actual_seps >= 2:
                parsed = parse_simple_table_block(block)
                if parsed:
                    headers, rows = parsed
                    pipe_lines = table_to_pipe(headers, rows)
                    result.extend(pipe_lines)
                else:
                    result.extend(block)
            else:
                result.extend(block)
        else:
            result.append(lines[i])
            i += 1

    return '\n'.join(result)


def _looks_like_table_content(line, block):
    """Heuristic: does this line look like it belongs to the table?"""
    stripped = line.strip()
    if not stripped:
        return True
    # Check if line has similar indentation to other content in block
    if line.startswith('  '):
        return True
    # Check for typical non-table indicators
    if stripped.startswith('#'):
        return False
    if stripped.startswith('```'):
        return False
    return False


def fix_file(filepath, dry_run=False):
    """Fix simple tables in a single file. Returns True if changes were made."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    # Quick check: does this file contain simple table separators?
    if not re.search(r'^\s*-{10,}[\s-]*$', original, re.MULTILINE):
        return False

    # Don't match YAML front matter delimiters
    fixed = convert_simple_tables(original)

    if fixed != original:
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed)
        return True
    return False


def fix_directory(dirpath, dry_run=False):
    """Fix simple tables in all .md files in directory (recursive)."""
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
            print("No simple tables found.")
    else:
        print(f"Not found: {target}")
        sys.exit(1)


if __name__ == '__main__':
    main()
