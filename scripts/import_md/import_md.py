#!/usr/bin/env python3

import os
import sys
import yaml
import logging
import requests


def import_text_section(section_id, filename):
    with open(filename, 'w') as f:
        f.write(f"Not implemented: {section_id}\n")


def import_image(url, filename):
    """
    Import an image from a URL and save it to a file.
    Use global HEADERS to include session token if needed.
    """
    logger.info(f"Downloading image from {url} to {filename}")
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Raise an error for bad responses
    with open(filename, 'wb') as f:
        f.write(response.content)


def import_item(path, item, order, t):
    if t == "HEADER":
        slug = item["slug"]
        title = item["title_ru"]
        path = os.path.join(path, slug)
        os.makedirs(path, exist_ok=True)
        make_md_file(
            filename=os.path.join(path, 'index.md'),
            title=title,
            order=order,
        )
        for i, child in enumerate(item.get("children", [])):
            import_item(path, child, i, child["type"])
    elif t == "TEXT":
        import_text_section(
            section_id=item["section_id"],
            filename=os.path.join(path, f"{item['slug']}.md")
        )
        if "images" in item:
            for i, item in enumerate(item["images"]):
                import_item(path, item, i, "IMAGE")
    elif t == "IMAGE":
        orig_path = item["orig_path"]
        filename = item["filename"]
        url = f"{BASE_URL}/{orig_path}"
        parent_path = os.path.dirname(path)
        # image path is public/{parent_path}/{filename}
        image_path = os.path.join('public', parent_path, filename)
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


# Set up logging
logger = logging.getLogger('import_md')


BASE_URL = os.environ.get('AISYSTANT_BASE_URL', 'https://api.aisystant.com/api')
AISYSTANT_SESSION_TOKEN = os.getenv('AISYSTANT_SESSION_TOKEN')
HEADERS = {'Session-Token': AISYSTANT_SESSION_TOKEN}

name = sys.argv[1]
yaml_file = f"metadata/yaml/{name}.yaml"

if not os.path.exists(yaml_file):
    logger.error(f"YAML file {yaml_file} does not exist.")
    sys.exit(1)

# Read the YAML file
with open(yaml_file, 'r') as file:
    try:
        data = yaml.safe_load(file)
        path = f'docs/ru/{name}'
        os.makedirs(path, exist_ok=True)
        make_md_file(
            filename=os.path.join(path, 'index.md'),
            title=data.get('course_name', 'Untitled'),
            body="",
        )
        for i, section in enumerate(data.get('sections', [])):
            import_item(path, section, i, section["type"])
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        sys.exit(1)
