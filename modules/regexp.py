from requests import get,Session
from re import match,findall
from rdflib import Graph,URIRef,Literal

def extract(url, uri, config={}):
    g = Graph()
    g.namespace_manager.bind('rdf', URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
    g.namespace_manager.bind('schema', URIRef('https://schema.org/'))
    g.add((URIRef(uri), URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), URIRef(config['type'])))

    # get page
    with Session() as session:
        r = session.get(url)
        text = r.text

        print(f'fetched {len(text)} bytes for URL {url} with status code {r.status_code}', flush=True)

        for pattern in config.get('patterns', []):
            print(pattern, findall(pattern['match'], text))
            for hit in findall(pattern['match'], text):
                g.add((URIRef(uri), URIRef(pattern['predicate']), Literal(hit)))
                #ret += [ [ uri, pattern['predicate'], hit ] ]

    return g
