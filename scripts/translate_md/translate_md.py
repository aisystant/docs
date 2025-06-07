#!/usr/bin/env python3

import os
import sys
import yaml
import logging
import re
from markdownify import markdownify as md

from langsmith import Client
from openai import OpenAI
from langchain_core.messages import convert_to_openai_messages


def translate_text(text, lang):
    """
    Translate the given text using the OpenAI API.
    """
    logging.info(f"Translating text: {text[:100]}... to {lang}")
    if lang != "en":
        raise NotImplementedError("Only English translation is supported.")
    doc = {
        "body": text,
    }
    formatted_prompt = prompt.invoke(doc)
    response = oai_client.chat.completions.create(
        model=model,
        messages=convert_to_openai_messages(formatted_prompt.messages),
        temperature=0,
    )
    translated_text = response.choices[0].message.content.strip()
    logging.info(f"Translated text: {translated_text[:100]}...")
    if not translated_text:
        logging.error("Translation returned an empty result.")
        sys.exit(1)
    return translated_text

def translate_text_section(section, order, stack):
    """
    Fetch section text from API, convert to markdown, update footnotes and image links, and write to file.
    """
    title = section.get("title_en")
    src_filename = os.path.join(build_path_for_md(stack, 'ru'), f"{section['slug']}.md")
    dst_filename = os.path.join(build_path_for_md(stack, 'en'), f"{section['slug']}.md")
    bak_filename = dst_filename.replace('docs/en/', 'docs/en/bak.')

    logging.info(f"Translating section: {title} from {src_filename} to {dst_filename}")

    # if the destination file already exists and force is not set, skip translation
    if not force and os.path.exists(bak_filename):
        logging.info(f"Skipping translation for {dst_filename} as it already exists.")
        # copy the existing file from the backup location
        os.makedirs(os.path.dirname(dst_filename), exist_ok=True)
        os.rename(bak_filename, dst_filename)
        return

    # read the source file
    with open(src_filename, 'r', encoding='utf-8') as f:
        raw = f.read()

    # get the text, without the front matter
    body = raw.split('---', 2)[2].strip()

    # remove the first header
    body = re.sub(r'^#.*\n?', '', body, count=1)

    # replace ](/ru/ with ](/en/
    body = re.sub(r'\]\(/ru/', r'](/en/', body)

    # translated_text = body
    translated_text = translate_text(body, 'en')
    #translated_text = re.sub(r'\s\[\s*\^(\d+)\s*\]', r'[^\1]', translated_text)
    #translated_text = re.sub(r'^---\n?', '', translated_text, flags=re.MULTILINE)

    make_md_file(
        filename=dst_filename,
        title=title,
        body=translated_text,
        order=order
    )


def import_item(stack, item, order, t):
    if t == "HEADER":
        slug = item["slug"]
        title = item["title_en"]
        path = build_path_for_md(stack + [slug], 'en')
        os.makedirs(path, exist_ok=True)
        make_md_file(
            filename=os.path.join(path, 'index.md'),
            title=title,
            order=order,
        )
        for i, child in enumerate(item.get("children", [])):
            import_item(stack + [slug], child, i, child["type"])
    elif t == "TEXT" or t == "TEST":
        translate_text_section(
            section=item,
            order=order,
            stack=stack
        )


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


def build_path_for_md(stack, lang):
    """
    Build a path for the markdown file based on the stack.
    """
    return os.path.join('docs', lang, *stack)


def build_path_for_images(stack, lang):
    """
    Build a path for the images based on the stack.
    """
    return os.path.join('docs', 'public', lang, stack[0])


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

force = len(sys.argv) > 2 and sys.argv[2] == '--force'

client = Client()           # LangSmith client
oai_client = OpenAI()       # OpenAI client
prompt = client.pull_prompt("translateprod")

model = "gpt-4.1"

# Read the YAML file
with open(yaml_file, 'r') as file:
    try:
        data = yaml.safe_load(file)
        stack = [name]
        os.makedirs(build_path_for_md(stack, 'en'), exist_ok=True)
        make_md_file(
            filename=os.path.join(build_path_for_md(stack, 'en'), 'index.md'),
            title=data.get('course_name_en', 'Untitled'),
            body="",
        )
        for i, section in enumerate(data.get('sections', [])):
            import_item(stack, section, i, section["type"])
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        sys.exit(1)
