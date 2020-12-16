#!/usr/bin/env python3

from flask import Flask,request,render_template,Response
from rdflib import ConjunctiveGraph
from json import loads,dumps,load
from importlib import import_module
from yaml import load as yload,FullLoader
from re import match,sub
from os.path import join
from contextlib import closing
from rdflib import Graph,URIRef
from urllib.parse import urlparse

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
config = yload(open(join(app.root_path, 'config.yml')).read(), Loader=FullLoader)
app.jinja_env.line_statement_prefix = '#'
extractors = {}
cache = config.get('cache', False)
base = config['base']
store = None

if config.get('store', False):
    store = ConjunctiveGraph('Sleepycat')
    store.open(config['store'], create=True)


@app.route('/')
def index():
    j = sparql('select ?class (count(?class) as ?count) where {?s a ?class } group by ?class order by DESC(?count)')
 
    return render_template('index.html', counts=j, base=base)


@app.route('/_sparql')
def sparql_view():
    result = None
    query = request.args.get('query', None)

    if query:
        try:
            result = sparql(query)
        except Exception as e:
            return render_template('sparql.html', base=base, ex=e)

    return render_template('sparql.html', result=result, base=base, title='SPARQL')


@app.route('/<path:path>')
def resource_view(path):
    uri = f'{base}{path}'
    j = get_json(uri)
    related_map = { x['@id']:x for x in j.get('relation', []) } if j else {}

    return render_template('resource.html', uri=uri, rdf=j, related_map=related_map, base=base) if j else ("Not found", 404)


@app.route('/<path:path>.ttl')
def turtle_view(path):
    rdf = get_triples(f'{base}{path}')

    return Response(rdf.serialize(format="turtle").decode("utf-8"), mimetype='text/turtle') if rdf else ("Not found", 404)


@app.route('/<path:path>.jsonld')
def jsonld_view(path):
    j = get_json(f'{base}{path}')

    return Response(dumps(j, indent=2), mimetype='application/json') if j else ("Not found", 404)


@app.route('/<path:path>.xml')
def xml_view(path):
    rdf = get_triples(f'{base}{path}')

    return Response(rdf.serialize(format="xml").decode("utf-8"), mimetype='application/xml') if rdf else ("Not found", 404)


def sparql(query):
    return loads(store.query(query).serialize(format='json').decode('utf-8'))
    

def get_json(uri):
    rdf = get_triples(uri)

    if rdf:
        context = {"@vocab": "https://schema.org/", "relation": "http://purl.org/dc/terms/relation" }
        j = loads(rdf.serialize(format="json-ld", context=context).decode("utf-8"))

        return frame_hack(j, uri)

    return None


def get_triples(uri):
    rdf = None

    if cache:
        ctx = store.get_context(uri)
        
        if ctx:
            # There has to be a better way!
            g = Graph()
            g.namespace_manager.bind('schema', URIRef('https://schema.org/'))
            for t in ctx:
                g.add(t)

            return g

    url_parts = urlparse(uri)

    for u in config.get('urls', []):
        m = match(u['match'], url_parts.path[1:])

        # find target URL
        if m:
            url = u['target'].format(**m.groupdict())

            # extract RDF
            if url:
                extractor = get_extractor(u.get('mode', 'rdfa'))
                rdf = extractor(url, uri, config=u.get('config', {}), base=base)
                break

    if rdf and store:
        for t in rdf:
            store.add((t[0], t[1], t[2], uri))

    return rdf


@app.route('/favicon.ico')
def favicon():
    return 'NO!',404


def load_extractor(name):
    module = import_module(f'modules.{name}')
    f = module.extract
    extractors[name] = f

    return f


def get_extractor(name):
    return extractors.get(name, load_extractor(name))


def frame_hack(j, uri):
    ret = { '@context': j['@context'] }
    main = next((x for x in j['@graph'] if x['@id'] == uri), None)
    ret.update(main)
    ret['relation'] = [ x for x in j['@graph'] if x['@id'] != uri ]

    return ret


