#    BSD license.

import networkx as nx

__all__ = ['cytojs_data', 'cytojs_graph']


# CytoscapeJs description
_attrs = dict(group='group', id='id', parent='parent',
              scratch='scratch', position='position', x='x', y='y',
              selected='selected', selectable='selectable',
              locked='locked', grabbable='grabbable', classes='classes',
              source='source', target='target',
              renderedPosition='renderedPosition')


def get_element(i, j, attrs):
    n = dict()
    n["data"] = j.copy()

    # Take the node/edge ID if present, or tries to use its name
    # An edge will be named by source->target, and a node will be named
    # by its networkx name IF this name is a str

    i = j.get(attrs["id"]) or (
        "{}->{}".format(i[0], i[1]) if isinstance(i, tuple) else i)
    if not isinstance(i, str):
        raise TypeError("Expected str, got {} !".format(type(i)))
    n["data"]["id"] = i

    if attrs["parent"] in j:
        n["data"]["parent"] = j.get(attrs["parent"], None)
    if attrs["source"] in j:
        n["data"]["source"] = j.get(attrs["source"], None)
    if attrs["source"] in j:
        n["data"]["target"] = j.get(attrs["target"], None)

    n["scratch"] = j.get(attrs["scratch"], None)
    n["selected"] = j.get(attrs["selected"], None)
    n["selectable"] = j.get(attrs["selectable"], None)
    n["locked"] = j.get(attrs["locked"], None)
    n["grabbable"] = j.get(attrs["grabbable"], None)
    n["classes"] = j.get(attrs["classes"], None)

    if attrs["position"] in j:
        n["position"] = {}
        n["position"]["x"] = j.get(attrs["position"], {}).get("x", None)
        n["position"]["y"] = j.get(attrs["position"], {}).get("y", None)
    if attrs["renderedPosition"] in j:
        n["renderedPosition"] = {}
        n["renderedPosition"]["x"] = j.get(
            attrs["renderedPosition"], {}).get("x", None)
        n["renderedPosition"]["y"] = j.get(
            attrs["renderedPosition"], {}).get("y", None)
    return clean_recur(n)


def clean_recur(dic):
    d = dict()
    for k, v in dic.items():
        if isinstance(v, dict):
            v = clean_recur(v)
        if v or v == 0:
            d[k] = v
    return d


def get_data(elem, attrs):
    n = elem.get("data", {}).copy()

    if attrs["id"] in elem.get("data", {}):
        n[attrs["id"]] = elem.get("data", {}).get("id", None)
    if attrs["parent"] in elem.get("data", {}):
        n[attrs["parent"]] = elem.get("data", {}).get("parent", None)
    if attrs["source"] in elem.get("data", {}):
        n[attrs["source"]] = elem.get("data", {}).get("source", None)
    if attrs["target"] in elem.get("data", {}):
        n[attrs["target"]] = elem.get("data", {}).get("target", None)

    n[attrs["scratch"]] = elem.get("scratch", None)
    n[attrs["selected"]] = elem.get("selected", None)
    n[attrs["selectable"]] = elem.get("selectable", None)
    n[attrs["locked"]] = elem.get("locked", None)
    n[attrs["grabbable"]] = elem.get("grabbable", None)
    n[attrs["classes"]] = elem.get("classes", None)

    if attrs["position"] in elem:
        n[attrs["position"]] = {}
        n[attrs["position"]][attrs["x"]] = elem.get(
            "position", {}).get("x", None)
        n[attrs["position"]][attrs["y"]] = elem.get(
            "position", {}).get("y", None)
    if attrs["renderedPosition"] in elem:
        n[attrs["renderedPosition"]] = {}
        n[attrs["renderedPosition"]][attrs["x"]] = elem.get(
            "renderedPosition", {}).get("x", None)
        n[attrs["renderedPosition"]][attrs["y"]] = elem.get(
            "renderedPosition", {}).get("y", None)
    return clean_recur(n)


def cytojs_data(G, attrs=None):
    """Return data in CytoscapeJS JSON format (cyjs). Data contained in
    G's nodes will be extracted in the JSON 'data' field.
    Elements whose name is described in attrs (or is a default name in
    CytoscapeJS json format) will also be placed where they should be
    according to CytoscapeJS JSON format.

    Parameters
    ----------
    G : NetworkX Graph
    attrs : dict
        The item names to use

    Returns
    -------
    data: dict
        A dictionary with cyjs formatted data.
    Raises
    ------
    NetworkXError
        If values in attrs are not unique.
    """
    multigraph = G.is_multigraph()
    if not attrs:
        attrs = _attrs
    else:
        attrs.update(
            {k: v for (k, v) in _attrs.items() if k not in attrs})

    if len(set(attrs)) < len(set(_attrs)):
        raise nx.NetworkXError('Attribute names are not unique.')

    jsondata = dict()
    jsondata['data'] = list(G.graph.items())
    jsondata['directed'] = G.is_directed()
    jsondata['multigraph'] = multigraph
    jsondata['elements'] = {"nodes": [], "edges": []}

    for i, j in G.node.items():
        n = get_element(i, j, attrs)
        jsondata['elements']['nodes'].append(n)

    for i, j in G.edges():
        att = G.edge[i][j].copy()
        att["source"] = i
        att["target"] = j
        n = get_element((i, j), att, attrs)
        jsondata['elements']['edges'].append(n)
    return jsondata


def cytojs_graph(data, attrs=None):
    """Create a graph from a dict formatted as CytoscapeJS.
    Data is fetched by following cyjs keywords, and by copying the
    "data" field into the graph elements' data.

    Parameters
    ----------
    data : The dict extracted from cytoscapeJS json
    attrs : dict
        The item names to use
    """
    if not attrs:
        attrs = _attrs
    else:
        attrs.update(
            {k: v for (k, v) in _attrs.items() if k not in attrs})

    if len(set(attrs)) < len(set(_attrs)):
        raise nx.NetworkXError('Attribute names are not unique.')

    multigraph = data.get('multigraph')
    directed = data.get('directed')
    if multigraph:
        graph = nx.MultiGraph()
    else:
        graph = nx.Graph()
    if directed:
        graph = graph.to_directed()

    elems = data.get('elements', {})
    for e in elems.get("edges", {}):
        n = get_data(e, attrs)
        src = n.get(attrs["source"])
        dst = n.get(attrs["target"])
        del(n[attrs["source"]])
        del (n[attrs["target"]])
        graph.add_edge(src, dst, **n)

    for e in elems.get("nodes", {}):
        n = get_data(e, attrs)
        if n:
            graph.add_node(n.get(attrs["id"]), **n)
    return graph

