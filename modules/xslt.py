from requests import get,Session
from rdflib import Graph,URIRef,Literal
from lxml import etree,html
from os.path import realpath,dirname,join

def extract(url, uri, config={}):
    # get page
    with Session() as session:
        r = session.get(url)
        text = r.text

        print(f'fetched {len(text)} bytes for URL {url} with status code {r.status_code}', flush=True)

        # get DOM
        dom = html.document_fromstring(text)

        d = join(dirname(realpath(__file__)), '..', 'xsl')
        print(__file__, realpath(__file__), dirname(realpath(__file__)), d)
        with open(join(d, f'{config["xslt"]}.xsl'), mode='rb') as f:
            t = etree.XSLT(etree.parse(f))
            result = str(t(dom, uri=etree.XSLT.strparam(uri), url=etree.XSLT.strparam(url)))

            #print(str(dom))
            #print(result)

            g = Graph().parse(data=result)
            g.add((URIRef(uri), URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), URIRef(config['type'])))

            if url != uri:
                g.add((URIRef(url), URIRef('https://schema.org/mainEntity'), URIRef(uri)))

            return g

