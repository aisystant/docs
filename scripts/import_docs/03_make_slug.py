import requests
import logging
import os
import sys
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

def decode_base64(encoded_text):
    """
    Decodes a Base64-encoded string to plain text.
    """
    try:
        decoded_bytes = base64.b64decode(encoded_text)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decode Base64 text: {e}")
        return ""

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
        "model": model
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

def add_slug_to_structure(structure):
    """
    Recursively adds a slug to each element in the structure.
    """
    for element in structure:
        try:
            base64_text = element.get("text", "")
            decoded_text = decode_base64(base64_text)
        except Exception as e:
            decoded_text = ""
        title = element.get("title", "")
        if title:
            translated_title = translate_text(
                text=title,
                lang="en",
                system_prompt_cid="QmQNECrHspRRLxeq34uNWmxMmjDAtk5SGN11PApiP9idFk",
                user_prompt_cid="Qmcu6Tn9bZorQGt7gRvZ8JymmCcTGRkfX4ermAyKWnkEyx",
                context=decoded_text,
                model="gpt-4o"
            )
            element["slug"] = slugify(translated_title)
            element["english_title"] = title
        else:
            element["slug"] = ""
        if "children" in element:
            add_slug_to_structure(element["children"])

if __name__ == "__main__":
    try:
        input_json = sys.stdin.read()
        structure = json.loads(input_json)
    except Exception as e:
        logger.error(f"Failed to read or parse input JSON: {e}")
        sys.exit(1)

    # Add slugs to the structure
    try:
        add_slug_to_structure(structure)
    except Exception as e:
        logger.error(f"An error occurred while processing the structure: {e}")
        sys.exit(1)

    # Output the updated structure
    print(json.dumps(structure, indent=4, ensure_ascii=False))
