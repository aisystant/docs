#!/bin/env python3

import requests
import logging
import os
import sys
import yaml
import json
import base64
from slugify import slugify
from langsmith import Client
from openai import OpenAI
from langchain_core.messages import convert_to_openai_messages


# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


filename = sys.argv[1]
logger.info(f"Translating file: {filename}")
if not filename.endswith(".md"):
    logger.error("Only markdown files are translatable.")
    sys.exit(1)


ORIG_LANG = "ru"
DST_LANG = ["en"]


client = Client()           # LangSmith client
oai_client = OpenAI()       # OpenAI client

prompt = client.pull_prompt("translateprod")

TITLE_CACHE_FILE = "title.yaml"


def load_title_cache():
    """Load the translation cache from the YAML file."""
    if os.path.exists(TITLE_CACHE_FILE):
        try:
            with open(TITLE_CACHE_FILE, "r", encoding="utf-8") as f:
                cache = yaml.safe_load(f)
                return cache if isinstance(cache, dict) else {}
        except Exception as e:
            logger.error(f"Failed to load cache from {TITLE_CACHE_FILE}: {e}")
            return {}
    return {}


title_cache = load_title_cache()


def get_title_from_cache(title, lang):
    """
    Retrieve the translated title from the cache.
    """
    if lang != "en":
        raise NotImplementedError("Only English translation is supported.")
    return title_cache[title]

def translate_text(text, lang):
    """
    Translate the given text using the OpenAI API.
    """
    logger.info(f"Translating text: {text[:100]}... to {lang}")
    if lang != "en":
        raise NotImplementedError("Only English translation is supported.")
    doc = {
        "body": text,
    }
    formatted_prompt = prompt.invoke(doc)
    response = oai_client.chat.completions.create(
        model="gpt-4o",  # Change to "gpt-4" if needed
        messages=convert_to_openai_messages(formatted_prompt.messages)
    )
    translated_text = response.choices[0].message.content.strip()
    logger.info(f"Translated text: {translated_text[:100]}...")
    if not translated_text:
        logger.error("Translation returned an empty result.")
        sys.exit(1)
    return translated_text


for lang in DST_LANG:
    with open(filename, "r") as f:
        content = f.read()
    out_filename = filename.replace(ORIG_LANG, lang)
    output_directory = os.path.dirname(out_filename)
    # skip if file already exists
    if os.path.exists(out_filename):
        logger.info(f"File {out_filename} already exists. Skipping translation.")
        continue
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    # if markdown file
    if filename.endswith(".md"):
        frontmatter = content.split("---")[1]
        body = content.split("---")[2]
        info = yaml.safe_load(frontmatter)
        logger.info(f"Frontmatter: {info}")
        logger.info(f"Translating title: {info['title']}")
        title = get_title_from_cache(info["title"], lang)
        logger.info(f"Translated title: {title}")
        info["title"] = title
        frontmatter = yaml.dump(info, default_flow_style=False)
        if body.strip() != "":
            body = translate_text(body, lang)
        # content should be bytes
        content = "---\n" + frontmatter + "---\n\n" + body
        content = content.encode("utf-8")
    with open(out_filename, "wb") as out_f:
        out_f.write(content)
