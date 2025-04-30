import os
import re
import yaml

DOCS_DIR = "./docs"  # Root directory containing markdown files

def process_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    # Match YAML frontmatter and body
    match = re.match(r'(?s)^---\n(.*?)\n---\n(.*)$', content)
    if not match:
        print(f"Skipped (no frontmatter): {filepath}")
        return

    frontmatter_raw, body = match.groups()

    try:
        frontmatter = yaml.safe_load(frontmatter_raw)
    except yaml.YAMLError as e:
        print(f"Skipped (invalid YAML): {filepath}")
        return

    title = frontmatter.get("title")
    if not title or not isinstance(title, str):
        print(f"Skipped (no valid title): {filepath}")
        return

    # Check if the body already starts with the title as a heading
    if body.lstrip().startswith(f"# {title}"):
        print(f"Already has heading: {filepath}")
        return

    # Prepend the heading to the body
    new_body = f"# {title}\n\n{body.lstrip()}"
    new_content = f"---\n{frontmatter_raw}\n---\n\n{new_body}"

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(new_content)

    print(f"Updated: {filepath}")

def process_all_markdown_files(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.lower().endswith(".md"):
                filepath = os.path.join(root, filename)
                process_markdown_file(filepath)

if __name__ == "__main__":
    process_all_markdown_files(DOCS_DIR)