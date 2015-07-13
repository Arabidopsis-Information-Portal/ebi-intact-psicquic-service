import requests
import re
import urlparse
import json

EBI_INTACT_BASE_URL = 'http://www.ebi.ac.uk/Tools/webservices/psicquic/intact/webservices/current/search/query/'

def is_valid_agi_identifier(ident):
    p = re.compile(r'AT[1-5MC]G[0-9]{5,5}\.[0-9]+', re.IGNORECASE)
    if not p.search(ident):
        return False
    return True

def do_request(search_term):
    """Perform a request to SITE and return response."""

    url = urlparse.urljoin(EBI_INTACT_BASE_URL, search_term)
    response = requests.get(url, verify=False, stream=True)

    # Raise exception and abort if requests is not successful
    response.raise_for_status()

    return response

def send(data):
    """Display `data` in the format required by Adama.
    :type data: list
    """

    for elt in data:
        print json.dumps(elt)
        print '---'

def fail(message):
    # failure message for generic adapters
    return 'text/plaintext; charset=ISO-8859-1', message
