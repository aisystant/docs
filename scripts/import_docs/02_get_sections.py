import requests
import logging
import os
import sys
import json
import base64
import re
from markdownify import markdownify as md

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

BASE_URL = 'https://api.aisystant.com/api'
AISYSTANT_SESSION_TOKEN = os.getenv('AISYSTANT_SESSION_TOKEN')
HEADERS = {'Session-Token': AISYSTANT_SESSION_TOKEN}

FOOTNOTE_PATTERN = re.compile(
    r'<span class="sspopup".*?><sup>\d+</sup><span class="sspopuptext".*?>(.*?)</span></span>',
    re.DOTALL
)

IMAGE_PATTERN = re.compile(
    r'<img\s+src="(.*?)"\s+alt=".*?">', 
    re.DOTALL
)

def replace_footnotes(html):
    """
    Replaces footnotes in the HTML text with the format {{beginfootnote}}...{{endfootnote}}.
    """
    def footnote_replacer(match):
        content = match.group(1).strip().replace("[x] ", "")
        return f"{{{{beginfootnote}}}}{content}{{{{endfootnote}}}}"

    return FOOTNOTE_PATTERN.sub(footnote_replacer, html)

def extract_attachments(html):
    """
    Extracts all image attachments from the HTML text.
    """
    return IMAGE_PATTERN.findall(html)

def send_get_request(path):
    """
    Sends a GET request to the specified API endpoint.
    """
    url = f'{BASE_URL}/{path}'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.content.decode('utf-8', errors='replace')
    except requests.RequestException as e:
        logger.error(f"Error while sending GET request to {url}: {e}")
        return ""

def fetch_text(section_id):
    """
    Fetches the text content for a section based on its ID, processes footnotes and attachments.
    """
    raw_html = send_get_request(f'courses/text/{section_id}')
    html_with_replaced_footnotes = replace_footnotes(raw_html)
    attachments = extract_attachments(raw_html)
    markdown_text = md(html_with_replaced_footnotes)
    return {
        "text": base64.b64encode(markdown_text.encode()).decode(),
        "attachments": attachments
    }

def add_text_to_structure(structure):
    """
    Recursively adds text and attachments to each element in the structure.
    """
    for element in structure:
        fetched_data = fetch_text(element["id"])
        element["text"] = fetched_data["text"]
        if fetched_data["attachments"]:
            element["attachments"] = fetched_data["attachments"]
        if "children" in element:
            add_text_to_structure(element["children"])

if __name__ == "__main__":
    try:
        input_json = sys.stdin.read()
        structure = json.loads(input_json)
    except Exception as e:
        logger.error(f"Failed to read or parse input JSON: {e}")
        sys.exit(1)

    # Add text content and attachments to the structure
    add_text_to_structure(structure)

    # Output the updated structure
    print(json.dumps(structure, indent=4, ensure_ascii=False))