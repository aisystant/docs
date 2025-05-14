import requests
import logging
import os
import re
import sys
import json

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

def send_get_request(path):
    url = f'{BASE_URL}/{path}'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error while sending GET request to {url}: {e}")
        return None

def get_course_structure(version_id):
    try:
        return send_get_request(f'courses/course-versions/{version_id}')
    except Exception as e:
        logger.error(f"Failed to fetch course structure for version ID {version_id}: {e}")
        return None


def remove_number_prefix(text):
    return re.sub(r'^\d+\.\s*', '', text)


def build_hierarchical_structure(sections):
    result = []
    current_header = None
    #relative_order = 0

    for section in sections:
        section_data = {
            "type": section["type"].lower(),
            "title": remove_number_prefix(section["title"]),
            "id": section["id"],
        }

        if section["type"] == "HEADER":
            current_header = section_data
            current_header["children"] = []
            current_header["order"] = len(result)
            result.append(current_header)
        else:
            if current_header:
                childrens = current_header["children"]
                section_data["order"] = len(childrens)
                current_header["children"].append(section_data)
            else:
                section_data["order"] = len(result)
                result.append(section_data)

    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Version ID is a required argument.")
        sys.exit(1)

    version_id = sys.argv[1]
    course_data = get_course_structure(version_id)

    if course_data and "sections" in course_data:
        hierarchical_structure = build_hierarchical_structure(course_data["sections"])
        print(json.dumps(hierarchical_structure, indent=4, ensure_ascii=False))
    else:
        logger.error(f"Failed to fetch or process sections for version ID {version_id}")
        sys.exit(1)
