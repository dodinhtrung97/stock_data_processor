from contextlib import closing
from requests import get
from requests.exceptions import RequestException

import logging

LOGGER = logging.getLogger(__name__)

def get_html_response(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    Return text content if response is of type HTML/XML
    Return None otherwise
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        LOGGER.error(f'Error during requests to {url} : {str(e)}')
        return None


def is_good_response(resp):
    """
    Check if is good repsonse on get_html_response
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)