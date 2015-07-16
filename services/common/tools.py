import requests
import re
import urlparse
import json

EBI_INTACT_BASE_URL = 'http://www.ebi.ac.uk/Tools/webservices/psicquic/intact/webservices/current/search/query/'
DATABASE_URLS = {'uniprotkb': 'http://www.uniprot.org/uniprot/',
                 'intact': 'http://www.ebi.ac.uk/intact/',
                 'taxid': 'http://www.uniprot.org/taxonomy/',
                 'psi-mi': 'http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=',
                 'pubmed': 'http://www.ncbi.nlm.nih.gov/pubmed/'}

class MITabTextDecoder:
    def __init__(self, text):
        self.buffer = text if text else ""
        self.offset = 0

    def nextToken(self, delimiter):
        token = ''
        if (self.offset < len(self.buffer)):
            start = self.offset
            index = self.buffer.find(delimiter, start)
            if (index != -1):
                self.offset = index
                token = self.buffer[start:index]
                self.offset += len(delimiter)
            else:
                self.offset = len(self.buffer)
                token = self.buffer[start:]
        return token

    def hasNext(self):
        return self.offset < len(self.buffer)

    def decodeXref(self):
        xref = {'key':'', 'value':'', 'desc':''}
        token = self.nextToken(':')
        if (len(token) > 1):
            xref['key'] = token
            xref['value'] = self.nextToken('|').replace('"','')
            descIndex = xref['value'].find('(')
            if (descIndex != -1):
                xref['desc'] = xref['value'][descIndex+1:len(xref['value'])-1]
                xref['value'] = xref['value'][0:descIndex]
        return xref

def getProteinXref(text):
    protein_xref = {'id': '', 'url': ''}
    ids = []
    urls = []
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        ids.append(xref['value'])
        if DATABASE_URLS.has_key(xref['key']):
            base_url = DATABASE_URLS[xref['key']]
            urls.append("%s%s" % (base_url, xref['value']))
        else:
            urls.append(xref['key']+":"+xref['value'])
    if (len(ids) > 0):
        protein_xref['id'] = ", ".join(ids)
        protein_xref['url'] = ", ".join(urls)
    return protein_xref

def getInteractionXref(text):
    interaction_xref = {'id': '', 'url': ''}
    ids = []
    urls = []
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        ids.append(xref['value'])
        if DATABASE_URLS.has_key(xref['key']):
            base_url = DATABASE_URLS[xref['key']]
            urls.append("%sinteraction/%s" % (base_url, xref['value']))
        else:
            urls.append(xref['key']+":"+xref['value'])
    if (len(ids) > 0):
        interaction_xref['id'] = ", ".join(ids)
        interaction_xref['url'] = ", ".join(urls)
    return interaction_xref

def getValueXref(text):
    value_xref = {'id': '', 'url': ''}
    ids = []
    urls = []
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        val = xref['key'] + ':' + xref['value']
        ids.append(val)
        if DATABASE_URLS.has_key(xref['key']):
            base_url = DATABASE_URLS[xref['key']]
            urls.append("%s%s" % (base_url, xref['value']))
        else:
            urls.append(val)
    if (len(ids) > 0):
        value_xref['id'] = ", ".join(ids)
        value_xref['url'] = ", ".join(urls)
    return value_xref

def getValue(text):
    value = ''
    values = []
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        values.append(xref['value'])
    if (len(values) > 0):
        value = ", ".join(values)
    return value

def getRawValue(text):
    value = ''
    decoder = MITabTextDecoder(text)
    if decoder.hasNext():
        xref = decoder.decodeXref()
        value = xref['value']
    return value

def getDescriptionValueXref(text):
    desc_xref = {'id': '', 'url': ''}
    ids = []
    urls = []
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        ids.append(xref['desc'])
        if DATABASE_URLS.has_key(xref['key']):
            base_url = DATABASE_URLS[xref['key']]
            urls.append("%s%s" % (base_url, xref['value']))
        else:
            urls.append(xref['key']+":"+xref['value'])
    if (len(ids) > 0):
        desc_xref['id'] = ", ".join(ids)
        desc_xref['url'] = ", ".join(urls)
    return desc_xref

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
