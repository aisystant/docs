import os
import sys
import json
import base64
import logging
import re
import requests
from urllib.parse import urlsplit, unquote

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

AISYSTANT_BASE_URL = os.environ.get('AISYSTANT_BASE_URL', 'https://api.aisystant.com/api')
AISYSTANT_SESSION_TOKEN = os.getenv('AISYSTANT_SESSION_TOKEN')
HEADERS = {'Session-Token': AISYSTANT_SESSION_TOKEN}

FOOTNOTE_BEGIN = "{{beginfootnote}}"
FOOTNOTE_END = "{{endfootnote}}"
FOOTNOTE_PATTERN = re.compile(rf"\{FOOTNOTE_BEGIN}(.*?)\{FOOTNOTE_END}")

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

def sanitize_filename(name):
    """
    Ensures a safe filename by removing invalid characters.
    """
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()

def replace_footnotes(text):
    """
    Replaces custom footnote tags with Markdown footnote format.
    """
    return FOOTNOTE_PATTERN.sub(r"^[\1]", text)

def download_and_replace_attachments(text, attachments, section_name, output_dir):
    """
    Downloads attachments, saves them with new names, and replaces links in the text.
    """
    logger.info(f"Downloading attachments for section {section_name}, attachments: {attachments}, output_dir: {output_dir}")
    for attachment_url in attachments:
        try:
            # Extract original filename and extension
            original_filename = os.path.basename(urlsplit(attachment_url).path)
            name, ext = os.path.splitext(original_filename)
            new_filename = f"{section_name}-{name}{ext}"
            local_path = os.path.join(output_dir, new_filename)

            # Correct the attachment URL to remove double slashes
            attachment_url = f"{AISYSTANT_BASE_URL}/{attachment_url.lstrip('/')}"
            
            # Download the file
            response = requests.get(attachment_url, headers=HEADERS, stream=True)
            response.raise_for_status()
            with open(local_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            # Replace the URL in the text with the relative path
            text = text.replace(attachment_url, f"./{new_filename}")
            logger.info(f"Downloaded and saved attachment: {local_path}")
        except requests.RequestException as e:
            logger.error(f"Failed to download attachment {attachment_url}: {e}")

    return text

def write_structure_to_files(structure, base_dir):
    """
    Recursively writes the structure to files and folders, including frontmatter and attachments.
    """
    for element in structure:
        # Get title, order, and text
        slug = element.get("slug", "untitled")
        title = element.get("title", "Untitled")
        order = element.get("order", 0)
        text_base64 = element.get("text", "")
        decoded_text = decode_base64(text_base64)
        section_name = sanitize_filename(slug)

        # Process footnotes
        decoded_text = replace_footnotes(decoded_text)

        # Process attachments if present
        if "attachments" in element:
            decoded_text = download_and_replace_attachments(decoded_text, element["attachments"], section_name, base_dir)

        # If the element is a header, use "index.md" as filename
        if element.get("type", "").lower() == "header":
            element_path = os.path.join(base_dir, section_name)
            os.makedirs(element_path, exist_ok=True)
            file_path = os.path.join(element_path, "index.md")
        else:
            # For text elements, use slug as filename
            file_path = os.path.join(base_dir, f"{section_name}.md")

        # Write the content to the file
        with open(file_path, "w", encoding="utf-8") as file:
            # Write frontmatter
            file.write("---\n")
            file.write(f"title: \"{title}\"\n")
            file.write(f"order: {order}\n")
            file.write("---\n\n")
            # Write the content
            file.write(decoded_text)
        logger.info(f"Created file: {file_path}")

        # Process children if they exist
        if "children" in element:
            write_structure_to_files(element["children"], element_path if element.get("type", "").lower() == "header" else base_dir)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Target directory is a required argument.")
        print("Usage: python write_structure.py <output_directory>")
        sys.exit(1)

    output_directory = sys.argv[1]
    try:
        os.makedirs(output_directory, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create output directory {output_directory}: {e}")
        sys.exit(1)

    try:
        input_json = sys.stdin.read()
        structure = json.loads(input_json)
    except Exception as e:
        logger.error(f"Failed to read or parse input JSON: {e}")
        sys.exit(1)

    # Write the structure to files
    write_structure_to_files(structure, output_directory)
    logger.info(f"Structure written to {output_directory}")
