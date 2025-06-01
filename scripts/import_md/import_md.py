#!/usr/bin/env python3

import os
import sys
import yaml
import logging
import requests
import base64
import re
from markdownify import markdownify as md


FOOTNOTE_PATTERN = re.compile(
    r'<span class="sspopup".*?><sup>\d+</sup><span class="sspopuptext".*?>(.*?)</span></span>',
    re.DOTALL
)


def replace_footnotes(html):
    def footnote_replacer(match):
        content = match.group(1).strip().replace("[x] ", "")
        return f"{{{{beginfootnote}}}}{content}{{{{endfootnote}}}}"
    return FOOTNOTE_PATTERN.sub(footnote_replacer, html)


def replace_footnotes_markdown(text):
    """
    Replaces custom footnote tags with Markdown footnote format.
    """
    pattern = re.compile(r"\{\{beginfootnote\}\}(.*?)\{\{endfootnote\}\}", re.DOTALL)
    return pattern.sub(r"^[\1]", text)


def import_text_section(section, filename, order, stack):
    """
    Fetch section text from API, convert to markdown, update footnotes and image links, and write to file.
    """
    section_id = section.get("section_id")
    title = section.get("title_ru")
    url = f"{BASE_URL}/api/courses/text/{section_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    raw_html = response.content.decode('utf-8', errors='replace')
    html_with_replaced_footnotes = replace_footnotes(raw_html)
    markdown_text = md(html_with_replaced_footnotes)

    # Replace custom footnotes with markdown footnotes
    markdown_text = replace_footnotes_markdown(markdown_text)

    # Replace image URLs with correct local paths if images are present
    if "images" in section:
        course_name = stack[0] if stack else os.environ.get('COURSE_NAME', sys.argv[1])
        for img in section["images"]:
            orig_path = img["orig_path"]
            filename_img = img["filename"]
            rel_img_path = f"/ru/{course_name}/{filename_img}"
            markdown_text = markdown_text.replace(orig_path, rel_img_path)

    make_md_file(
        filename=filename,
        title=title,
        body=markdown_text,
        order=order
    )


def import_image(url, filename):
    """
    Import an image from a URL and save it to a file.
    Use global HEADERS to include session token if needed.
    """
    logging.info(f"Downloading image from {url} to {filename}")
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Raise an error for bad responses
    with open(filename, 'wb') as f:
        f.write(response.content)


def import_item(stack, item, order, t):
    if t == "HEADER":
        slug = item["slug"]
        title = item["title_ru"]
        path = build_path_for_md(stack + [slug])
        os.makedirs(path, exist_ok=True)
        make_md_file(
            filename=os.path.join(path, 'index.md'),
            title=title,
            order=order,
        )
        for i, child in enumerate(item.get("children", [])):
            import_item(stack + [slug], child, i, child["type"])
    elif t == "TEXT":
        path = build_path_for_md(stack)
        import_text_section(
            section=item,
            filename=os.path.join(path, f"{item['slug']}.md"),
            order=order,
            stack=stack
        )
        if "images" in item:
            for i, item in enumerate(item["images"]):
                import_item(stack, item, i, "IMAGE")
    elif t == "IMAGE":
        orig_path = item["orig_path"]
        filename = item["filename"]
        url = f"{BASE_URL}/{orig_path}"
        image_path = os.path.join(build_path_for_images(stack), filename)
        logging.info(f"Importing image from {url} to {image_path}")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        import_image(url, image_path)


def make_md_file(filename, title, body="", order=None):
    """
    Create an index file with the given title and body.
    """
    with open(filename, 'w') as f:
        f.write('---\n')
        f.write(f'title: "{title}"\n')
        if order is not None:
            f.write(f'order: {order}\n')
        f.write('---\n\n')
        f.write(f'# {title}\n\n')
        f.write(body)


def build_path_for_md(stack):
    """
    Build a path for the markdown file based on the stack.
    """
    return os.path.join('docs', 'ru', *stack)


def build_path_for_images(stack):
    """
    Build a path for the images based on the stack.
    """
    return os.path.join('docs', 'public', 'ru', stack[0])


# Set up logging
logging.basicConfig(level=logging.INFO)

logging.info('Starting import process')

BASE_URL = os.environ.get('AISYSTANT_BASE_URL', 'https://api.aisystant.com/api')
AISYSTANT_SESSION_TOKEN = os.getenv('AISYSTANT_SESSION_TOKEN')
HEADERS = {'Session-Token': AISYSTANT_SESSION_TOKEN}

name = sys.argv[1]
yaml_file = f"metadata/yaml/{name}.yaml"

if not os.path.exists(yaml_file):
    logging.error(f"YAML file {yaml_file} does not exist.")
    sys.exit(1)

# Read the YAML file
with open(yaml_file, 'r') as file:
    try:
        data = yaml.safe_load(file)
        stack = [name]
        os.makedirs(build_path_for_md(stack), exist_ok=True)
        make_md_file(
            filename=os.path.join(build_path_for_md(stack), 'index.md'),
            title=data.get('course_name', 'Untitled'),
            body="",
        )
        for i, section in enumerate(data.get('sections', [])):
            import_item(stack, section, i, section["type"])
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        sys.exit(1)
