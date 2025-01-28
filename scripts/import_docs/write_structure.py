import os
import sys
import json
import base64
import logging

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

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
    Sanitizes a string to use it as a safe filename.
    """
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()

def write_structure_to_files(structure, base_dir):
    """
    Recursively writes the structure to files and folders, including frontmatter.
    """
    for element in structure:
        # Get slug, title, and order
        slug = element.get("slug", "untitled")
        title = element.get("title", "Untitled")
        order = element.get("order", 0)
        text_base64 = element.get("text", "")
        decoded_text = decode_base64(text_base64)

        element_path = os.path.join(base_dir, sanitize_filename(slug))

        # If the element has children, create a folder
        if "children" in element:
            os.makedirs(element_path, exist_ok=True)
            logger.info(f"Created directory: {element_path}")
            write_structure_to_files(element["children"], element_path)
        else:
            # Otherwise, write the decoded text to a Markdown file
            file_path = f"{element_path}.md"
            with open(file_path, "w", encoding="utf-8") as file:
                # Write frontmatter
                file.write("---\n")
                file.write(f"title: \"{title}\"\n")
                file.write(f"order: {order}\n")
                file.write("---\n\n")
                # Write the content
                file.write(decoded_text)
            logger.info(f"Created file: {file_path}")

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
