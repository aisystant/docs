#!/bin/env python3

import requests
import logging
import os
import sys
import yaml
import json
import base64
from slugify import slugify

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

TRANSLATION_SERVICE_URL = "https://congenial-fishstick-4jqpgxv69h5r4w-5000.app.github.dev/api/translate"  # Translation service URL
AISYSTANT_SESSION_TOKEN = os.getenv('AISYSTANT_SESSION_TOKEN')
HEADERS = {'Session-Token': AISYSTANT_SESSION_TOKEN}

ORIG_LANG = "ru"
DST_LANG = ["en"]

TRANSLATE_TITLE_SYSTEM_PROMPT_CID = "QmQNECrHspRRLxeq34uNWmxMmjDAtk5SGN11PApiP9idFk"
TRANSLATE_TITLE_USER_PROMPT_CID = "Qmcu6Tn9bZorQGt7gRvZ8JymmCcTGRkfX4ermAyKWnkEyx"
TRANSLATE_BODY_SYSTEM_PROMPT_CID = "QmP6fwjoFK7uYrydDLnW4jieKULxrgkURrMLfLZeW22HNf"
TRANSLATE_BODY_USER_PROMPT_CID = "QmbJii88F64APCu4PrPRWNNhh7zfERrsBM6UehuDHiNJ8Q"


def translate_text(text, lang="en", system_prompt_cid="", user_prompt_cid="", context="", model="gpt-4o"):
    """
    Sends a request to the translation service to translate text.
    """
    payload = {
        "text": text,
        "lang": lang,
        "system_prompt_cid": system_prompt_cid,
        "user_prompt_cid": user_prompt_cid,
        "context": context,
        "model": model,
        "seed": 4
    }

    try:
        response = requests.post(
            TRANSLATION_SERVICE_URL,
            headers={"Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()
        translated_text = response.json().get("message", "")
        if not translated_text.strip():
            logger.error("Translation service returned an empty result.")
            sys.exit(1)
        return translated_text
    except requests.RequestException as e:
        logger.error(f"Failed to translate text '{text}': {e}")
        sys.exit(1)


filename = sys.argv[1]
logger.info(f"Translating file: {filename}")


for lang in DST_LANG:
    with open(filename, "r") as f:
        content = f.read()
    out_filename = filename.replace(ORIG_LANG, lang)
    output_directory = os.path.dirname(out_filename)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    # if markdown file
    if filename.endswith(".md"):
        frontmatter = content.split("---")[1]
        body = content.split("---")[2]
        info = yaml.safe_load(frontmatter)
        title = translate_text(info["title"], lang, context=body, 
                               system_prompt_cid=TRANSLATE_TITLE_SYSTEM_PROMPT_CID, 
                               user_prompt_cid=TRANSLATE_TITLE_USER_PROMPT_CID)
        info["title"] = title
        frontmatter = yaml.dump(info, default_flow_style=False)
        if body.strip() != "":
            body = translate_text(body, lang, system_prompt_cid=TRANSLATE_BODY_SYSTEM_PROMPT_CID, 
                                  user_prompt_cid=TRANSLATE_BODY_USER_PROMPT_CID)
        # content should be bytes
        content = "---\n" + frontmatter + "---\n\n" + body
        content = content.encode("utf-8")
    with open(out_filename, "wb") as out_f:
        out_f.write(content)
