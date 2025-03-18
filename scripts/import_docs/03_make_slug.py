import os
import sys
import json
import base64
import logging
import yaml
from slugify import slugify

# Import required libraries for LangSmith and OpenAI integration
from langsmith import Client
from openai import OpenAI
from langchain_core.messages import convert_to_openai_messages

# Setup logging configuration
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize LangSmith and OpenAI clients
client = Client()           # LangSmith client
oai_client = OpenAI()       # OpenAI client

# Pull the translation prompt from LangSmith (ensure that this prompt exists)
prompt = client.pull_prompt("translate-title")

# Path to the YAML file for caching translated titles
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

def save_title_cache(cache):
    """Save the translation cache to the YAML file."""
    try:
        with open(TITLE_CACHE_FILE, "w", encoding="utf-8") as f:
            yaml.dump(cache, f, allow_unicode=True)
    except Exception as e:
        logger.error(f"Failed to save cache to {TITLE_CACHE_FILE}: {e}")

# Load the title cache at startup
title_cache = load_title_cache()

def decode_base64(encoded_text):
    """
    Decode a Base64-encoded string to plain text.
    """
    try:
        decoded_bytes = base64.b64decode(encoded_text)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decode Base64 text: {e}")
        return ""

def translate_title(title, context=""):
    """
    Translate the title to English using LangSmith for prompt retrieval and OpenAI for generation.
    The result is cached and saved immediately after each new translation.
    """
    if title in title_cache:
        return title_cache[title]
    try:
        # Prepare the data for the prompt
        doc = {
            "title": title,
            "context": context
        }
        # Invoke the prompt to format the request
        formatted_prompt = prompt.invoke(doc)
        # Send the request to OpenAI by converting messages to the required format
        response = oai_client.chat.completions.create(
            model="gpt-4o",  # Change to "gpt-4" if needed
            messages=convert_to_openai_messages(formatted_prompt.messages)
        )
        translated_title = response.choices[0].message.content.strip()
        if not translated_title:
            logger.error("Translation returned an empty result.")
            sys.exit(1)
        # Cache the translation and immediately save the cache
        title_cache[title] = translated_title
        save_title_cache(title_cache)
        return translated_title
    except Exception as e:
        logger.error(f"Error translating title '{title}': {e}")
        sys.exit(1)

def add_slug_to_structure(structure):
    """
    Recursively add a slug (based on the translated title) to each element in the structure.
    """
    for element in structure:
        decoded_text = ""
        try:
            base64_text = element.get("text", "")
            decoded_text = decode_base64(base64_text)
        except Exception as e:
            logger.error(f"Error decoding text for element: {e}")

        title = element.get("title", "")
        if title:
            translated_title = translate_title(title, context=decoded_text)
            element["slug"] = slugify(translated_title)
            element["english_title"] = translated_title
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
        logger.error(f"Error processing the structure: {e}")
        sys.exit(1)

    # Output the updated structure
    print(json.dumps(structure, indent=4, ensure_ascii=False))