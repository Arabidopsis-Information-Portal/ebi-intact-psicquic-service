import requests
import re
import urlparse
import json
import itertools

EBI_INTACT_BASE_URL = 'http://www.ebi.ac.uk/Tools/webservices/psicquic/intact/webservices/current/search/query/'
DATABASE_URLS = {'uniprotkb': 'http://www.uniprot.org/uniprot/',
                 'intact': 'http://www.ebi.ac.uk/intact/',
                 'taxid': 'http://www.uniprot.org/taxonomy/',
                 'psi-mi': 'http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=',
                 'pubmed': 'http://www.ncbi.nlm.nih.gov/pubmed/',
                 'araport': 'https://apps.araport.org/thalemine/portal.do?class=Gene&externalids='}
LOCUS_DESC = 'locus name'
UNKNOWN_BASE = 'UNKNOWN_ID'
UNKNOWN_COUNTER = itertools.count().next

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

def nextUnknownValue():
    return "%s-%s" % (UNKNOWN_BASE, UNKNOWN_COUNTER())

def getProteinXref(text):
    protein_xrefs = []
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        if xref['value'] != '':
            record = { 'id': xref['value'], 'desc': xref['desc'] }
            if DATABASE_URLS.has_key(xref['key']):
                base_url = DATABASE_URLS[xref['key']]
                url = "%s%s" % (base_url, xref['value'])
            else:
                url = xref['key'] + ":" + xref['value']
            record['url'] = url
        else:
            record = { 'id': nextUnknownValue(), 'desc': '', 'url': '' }
        protein_xrefs.append(record)
    return protein_xrefs

def getInteractionXref(text):
    interaction_xrefs = []
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        record = { 'id': xref['value'] }
        if DATABASE_URLS.has_key(xref['key']):
            base_url = DATABASE_URLS[xref['key']]
            url = "%sinteraction/%s" % (base_url, xref['value'])
            record['desc'] = xref['value']
        else:
            url = xref['key'] + ":" + xref['value']
            record['desc'] = url
        record['url'] = url
        interaction_xrefs.append(record)
    return interaction_xrefs

def getValueXref(text):
    value_xrefs = []
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        record = { 'id': xref['value'] }
        if DATABASE_URLS.has_key(xref['key']):
            base_url = DATABASE_URLS[xref['key']]
            url = "%s%s" % (base_url, xref['value'])
            record['desc'] = xref['value']
        else:
            url = xref['key'] + ':' + xref['value']
            record['desc'] = url
        record['url'] = url
        value_xrefs.append(record)
    return value_xrefs

def getValue(text):
    values = []
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        if (xref['desc'] == LOCUS_DESC):
            locus_id = xref['value'].upper()
            base_url = DATABASE_URLS['araport']
            url = "%s%s" % (base_url, locus_id)
            record = { 'id': locus_id, 'desc': xref['desc'], 'url': url }
        else:
            record = { 'id': xref['value'], 'desc': xref['desc'], 'url': '' }
        values.append(record)
    return values

def getRawValue(text):
    value = ''
    decoder = MITabTextDecoder(text)
    if decoder.hasNext():
        xref = decoder.decodeXref()
        value = xref['value']
    return value

def getDescriptionValueXref(text):
    desc_xrefs = []
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        record = { 'id': xref['value'], 'desc': xref['desc'] }
        if DATABASE_URLS.has_key(xref['key']):
            base_url = DATABASE_URLS[xref['key']]
            url = "%s%s" % (base_url, xref['value'])
        else:
            url = xref['key'] + ":" + xref['value']
        record['url'] = url
        desc_xrefs.append(record)
    return desc_xrefs

def getScore(text):
    decoder = MITabTextDecoder(text)
    while decoder.hasNext():
        xref = decoder.decodeXref()
        if xref['key'] == 'intact-miscore':
            value = xref['value']
        else:
            value = '-'
    return value

def getLocus(text):
    decoder = MITabTextDecoder(text)
    record = None
    while decoder.hasNext():
        xref = decoder.decodeXref()
        if (xref['desc'] == LOCUS_DESC):
            locus_id = xref['value'].upper()
            base_url = DATABASE_URLS['araport']
            url = "%s%s" % (base_url, locus_id)
            record = { 'id': locus_id, 'desc': xref['desc'], 'url': url }
    return record

def createNodeRecord(ident, locus):
    record = { 'data': {
                   'id': ident['id'],
                   'name': ident['id'],
                   'url': ident['url'],
                   'locus': locus['id'] if locus else ident['id'],
                   'locus_url': locus['url'] if locus else ident['url']
                }
            }
    return record

def createEdgeRecord(id_a, id_b, fields):
    interaction_detect_methods = (getDescriptionValueXref(fields[6]))[0]
    score = getScore(fields[14])
    author = fields[7]
    publication = getValueXref(fields[8])
    sources = (getDescriptionValueXref(fields[12]))[0]
    sep = ", "

    record = { 'data': {
                  'source': id_a['id'],
                  'target': id_b['id'],
                  'interaction_detection_method_id': interaction_detect_methods['id'],
                  'interaction_detection_method_desc': interaction_detect_methods['desc'],
                  'confidence_score': score,
                  'first_author': author,
                  'publication': sep.join([p['id'] for p in publication]),
                  'source_database': sources['desc']
                }
            }
    return record

def isEdgeDuplicate(edges, edge):
    duplicate = False
    source = edge['data']['source']
    target = edge['data']['target']
    score = edge['data']['confidence_score']
    method = edge['data']['interaction_detection_method_id']
    for e in edges:
        if ( ((source == e['data']['source'] and target == e['data']['target']) or (target == e['data']['source'] and source == e['data']['target'])) and method == e['data']['interaction_detection_method_id'] and score == e['data']['confidence_score'] ):
            duplicate = True
    return duplicate

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
