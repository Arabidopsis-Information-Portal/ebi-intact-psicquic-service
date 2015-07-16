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
        record = {
                'locus': locus,
                'class': 'locus_property',
                'source_text_description': 'Molecular Interactions',
                'interaction_record': {
                    'unique_identifier_for_interactor_a': tools.getProteinXref(fields[0]),
                    'unique_identifier_for_interactor_b': tools.getProteinXref(fields[1]),
                    'alt_identifier_for_interactor_a': tools.getValue(fields[2]),
                    'alt_identifier_for_interactor_b': tools.getValue(fields[3]),
                    'aliases_for_a': tools.getValue(fields[4]),
                    'aliases_for_b': tools.getValue(fields[5]),
                    'interaction_detection_methods': tools.getDescriptionValueXref(fields[6]),
                    'first_author': fields[7],
                    'publication_identifier': tools.getValueXref(fields[8]),
                    'ncbi_tax_identifier_for_interactor_a': tools.getDescriptionValueXref(fields[9]),
                    'ncbi_tax_identifier_for_interactor_b': tools.getDescriptionValueXref(fields[10]),
                    'interaction_types': tools.getDescriptionValueXref(fields[11]),
                    'source_databases': tools.getDescriptionValueXref(fields[12]),
                    'interaction_identifiers_in_source': tools.getInteractionXref(fields[13]),
                    'confidence_score': tools.getRawValue(fields[14])
                }
            }
        print json.dumps(record, indent=2)
        print '---'

def list(args):
    raise Exception('not implemented yet')
