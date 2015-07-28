import json
import services.common.tools as tools

def search(args):
    """
    args contains a dict with one or key:values

    locus is AGI identifier and is mandatory
    """
    locus = args['locus'].upper()
    dedupe = args['dedupe']

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
    nodes = []
    edges = []
    proteins = {}
    for result in response.iter_lines():
        fields = result.strip().split('\t')
        id_a = (tools.getProteinXref(fields[0]))[0]
        id_b = (tools.getProteinXref(fields[1]))[0]
        locus_a = tools.getLocus(fields[4])
        locus_b = tools.getLocus(fields[5])

        # handle nodes
        if not proteins.has_key(id_a['id']):
            nodes.append(tools.createNodeRecord(id_a, locus_a))
            proteins[id_a['id']] = 1
        if not proteins.has_key(id_b['id']):
            nodes.append(tools.createNodeRecord(id_b, locus_b))
            proteins[id_b['id']] = 1

        # handle edges
        edge = tools.createEdgeRecord(fields)
        if dedupe:
            if not tools.isEdgeDuplicate(edges, edge):
                edges.append(edge)
        else:
            edges.append(edge)

    elements = { 'nodes': nodes, 'edges': edges}
    return 'application/json', json.dumps(elements)

def list(args):
    raise Exception('not implemented yet')
