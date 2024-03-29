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
from flask_caching import Cache

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
config = yload(open(join(app.root_path, 'config.yml')).read(), Loader=FullLoader)
app.jinja_env.line_statement_prefix = '#'
scache = Cache(app)
extractors = {}
cache = config.get('cache', False)
base = config['base']
store = None

if config.get('store', False):
    store = ConjunctiveGraph('Sleepycat')
    store.open(config['store'], create=True)


@app.route('/')
@scache.cached(timeout=300)
def index():
    #j = sparql('select ?class (count(?class) as ?count) where { ?s a ?class } group by ?class order by DESC(?count)')

    return render_template('index.html', counts=[], base=base, title=config.get('title', 'No title'), description=config.get('description', None), empty_message=config.get('empty_message', None))


@app.route('/_sparql')
def sparql_view():
    def wants_format(fmt):
        accept = request.headers.get('Accept', 'text/html')

        return any([ x.strip().startswith(fmt) for x in accept.split(',') ])

    result = None
    query = request.args.get('query', None)
    limit = request.args.get('limit', None)
    offset = request.args.get('offset', None)

    if query:
        q = query

        if 'LIMIT' not in query:
            if limit == None:
                limit = 10

            q += f' LIMIT {limit} '

        if 'OFFSET' not in query:
            if offset == None:
                offset = 0

            q += f' OFFSET {offset} '

        print(q)

        try:
            if wants_format('application/sparql-results+json') or request.args.get('format', 'html') == 'json':
                return Response(dumps(loads(store.query(query).serialize(format='json').decode('utf-8')), indent=2), mimetype='application/json')
            elif wants_format('application/sparql-results+xml') or request.args.get('format', 'html') == 'xml':
                return Response(store.query(query).serialize(format='xml').decode('utf-8'), mimetype='text/xml')

            result = store.query(q)
        except Exception as e:
            return render_template('sparql.html', base=base, ex=e)

    return render_template(
                'sparql.html',
                result=loads(result.serialize(format='json').decode('utf-8')) if query else None,
                base=base,
                title='SPARQL',
                query=query,
                limit=limit,
                offset=offset,
                examples=config.get('sparql_examples', []))


@app.route('/<path:path>')
def resource_view(path):
    uri = f'{base}{path}'
    j = get_json(uri)
    related_map = { x['@id']:x for x in j.get('@included', []) } if j else {}

    return render_template('resource.html', uri=uri, rdf=j, main_rdf={ k:v for k,v in j.items() if k != '@included' }, related_map=related_map, base=base) if j else ("Not found", 404)


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


def sparql(queryi, fmt='json'):
    return loads(store.query(query).serialize(format=fmt).decode('utf-8'))
    

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

    if rdf and store != None:
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
    ret['@included'] = [ x for x in j['@graph'] if x['@id'] != uri ]

    rel_map = { x['@id']:x for x in ret['@included'] }

    d=set()
    for key,value in ret.items():
        if isinstance(value, dict) and '@id' in value and value['@id'] in rel_map:
            value.update(rel_map[value['@id']])
            d.add(value['@id'])
        elif isinstance(value, list) and key != '@included':
            for v in value:
                if isinstance(v, dict) and '@id' in v and v['@id'] in rel_map:
                    v.update(rel_map[v['@id']])
                    d.add(v['@id'])

    ret['@included'] = [ x for x in rel_map.values() if x['@id'] not in d ]

    return ret


#@app.teardown_appcontext
#def teardown_db(exception):
#    if store != None:
#        print('Closing store ...')
#        store.close()

