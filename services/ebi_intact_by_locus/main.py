import json
import services.common.tools as tools

def search(args):
    """
    args contains a dict with one or key:values

    locus is AGI identifier and is mandatory
    """

    locus = args['locus'].upper()

    """
    Make the request to the remote service
    """
    response = tools.do_request(locus)

    """
    Iterate through the results
    Foreach record from the remote service, build the response json
    Print this json to stdout followed by a record separator "---"
    ADAMA takes care of serializing these results
    """
    for result in response.iter_lines():
        fields = result.strip().split('\t')
        ident_a = tools.getProteinXref(fields[0])
        ident_b = tools.getProteinXref(fields[1])
        int_detect_methods = tools.getDescriptionValueXref(fields[6])
        pub_ids = tools.getValueXref(fields[8])
        ncbi_tax_a = tools.getDescriptionValueXref(fields[9])
        ncbi_tax_b = tools.getDescriptionValueXref(fields[10])
        int_types = tools.getDescriptionValueXref(fields[11])
        source_db = tools.getDescriptionValueXref(fields[12])
        int_id_source = tools.getInteractionXref(fields[13])
        record = {
                'locus': locus,
                'class': 'locus_property',
                'source_text_description': 'Molecular Interactions',
                'interaction_record': {
                    'unique_identifier_for_interactor_a': ident_a['id'],
                    'unique_identifier_for_interactor_a_url': ident_a['url'],
                    'unique_identifier_for_interactor_b': ident_b['id'],
                    'unique_identifier_for_interactor_b_url': ident_b['url'],
                    'alt_identifier_for_interactor_a': tools.getValue(fields[2]),
                    'alt_identifier_for_interactor_b': tools.getValue(fields[3]),
                    'aliases_for_a': tools.getValue(fields[4]),
                    'aliases_for_b': tools.getValue(fields[5]),
                    'interaction_detection_methods': int_detect_methods['id'],
                    'interaction_detection_methods_url': int_detect_methods['url'],
                    'first_author': fields[7],
                    'publication_identifier': pub_ids['id'],
                    'publication_identifier_url': pub_ids['url'],
                    'ncbi_tax_identifier_for_interactor_a': ncbi_tax_a['id'],
                    'ncbi_tax_identifier_for_interactor_a_url': ncbi_tax_a['url'],
                    'ncbi_tax_identifier_for_interactor_b': ncbi_tax_b['id'],
                    'ncbi_tax_identifier_for_interactor_b_url': ncbi_tax_b['url'],
                    'interaction_types': int_types['id'],
                    'interaction_types_url': int_types['url'],
                    'source_databases': source_db['id'],
                    'source_databases_url': source_db['url'],
                    'interaction_identifiers_in_source': int_id_source['id'],
                    'interaction_identifiers_in_source_url': int_id_source['url'],
                    'confidence_score': tools.getRawValue(fields[14])
                }
            }
        print json.dumps(record, indent=2)
        print '---'

def list(args):
    raise Exception('not implemented yet')
