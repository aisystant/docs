#!/usr/bin/env python3

import os
import sys
import yaml
import logging
import requests


def import_text_section(section_id, filename, order):
    make_md_file(
        filename=filename,
        title=f"Section {section_id}",
        body=f"Content for section {section_id} goes here.",
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
        stack.append(slug)
        path = build_path_for_md(stack)
        os.makedirs(path, exist_ok=True)
        make_md_file(
            filename=os.path.join(path, 'index.md'),
            title=title,
            order=order,
        )
        for i, child in enumerate(item.get("children", [])):
            import_item(stack, child, i, child["type"])
    elif t == "TEXT":
        path = build_path_for_md(stack)
        import_text_section(
            section_id=item["section_id"],
            filename=os.path.join(path, f"{item['slug']}.md"),
            order=order
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
