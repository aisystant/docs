import requests
import logging
import os
import sys
import base64

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

BASE_URL = 'https://api.aisystant.com/api'
AISYSTANT_SESSION_TOKEN = os.getenv('AISYSTANT_SESSION_TOKEN', 'your_api_token_here')
HEADERS = {'Session-Token': AISYSTANT_SESSION_TOKEN}

def send_get_request(path, **kwargs):
    """Send a GET request to the specified path and return the response JSON."""
    url = f'{BASE_URL}/{path}'
    logger.debug(f"Sending GET request to {url} with headers {HEADERS}")
    response = requests.get(url, headers=HEADERS, **kwargs)
    response.raise_for_status()
    return response.json()

def get_courses_list():
    """Fetch the list of courses and return a list of course IDs with versions."""
    logger.info("Fetching the list of courses")
    try:
        courses = send_get_request('courses/courses')
        result = []
        for course in courses:
            course_id = course.get('productCode')
            version = course.get('activeVersion')
            versionId = course.get('activeVersionId')
            # changelog and authors will be base64 encoded
            authors = course.get("authors") or ""
            changelog = course.get("activeVersionChangeLog") or ""
            authors = base64.b64encode(authors.encode()).decode()
            changelog = base64.b64encode(changelog.encode()).decode()
            if not course_id or not version:
                continue
            result.append(f"{course_id}:{version}:{versionId}:{authors}:{changelog}")
        logger.info("Successfully fetched the courses list")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch courses list: {e}")
        return []


if __name__ == "__main__":
    courses_list = get_courses_list()
    if courses_list:
        for course in courses_list:
            print(course)
    else:
        sys.exit(1)
