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

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
config = yload(open(join(app.root_path, 'config.yml')).read(), Loader=FullLoader)
extractors = {}
cache = config.get('cache', False)

@app.route('/')
def index():
    host = request.headers.get('Host')
    base  = config.get('base', 'http://' + host + '/')
    title = config.get('title', base)

    return render_template('index.html', host=host, base=base, title=title)


@app.route('/_sparql')
def sparql():
    result = None    
    query = request.args.get('query', None)

    if query:
        with closing(get_store()) as store:
            result = store.query(query)
            
            return render_template('sparql.html', result=result, title='SPARQL')

    return render_template('sparql.html', result=None)



@app.route('/<path:path>')
def resource(path):
    proto = request.headers.get('Protocol', 'http')
    host = request.headers.get('Host')
    base = config.get('base', f'{proto}://{host}/')
    title = config.get('title', base)
    uri, url, rdf = f'{base}{path}',None,None

    rdf = get_resource(uri, path, base, '_reindex' not in request.args)

    return render_template('resource.html', rdf=rdf, host=host, base=base, title=title) if rdf else ("Not found", 404)


@app.route('/<path:path>.ttl')
def turtle(path):
    proto = request.headers.get('Protocol', 'http')
    host = request.headers.get('Host')
    base = config.get('base', f'{proto}://{host}/')
    uri, url,rdf = f'{base}{path}',None,None

    rdf = get_resource(uri, path, base, '_reindex' not in request.args)

    return Response(rdf.serialize(format="turtle").decode("utf-8"), mimetype='text/turtle') if rdf else ("Not found", 404)


@app.route('/<path:path>.jsonld')
def jsonld(path):
    proto = request.headers.get('Protocol', 'http')
    host = request.headers.get('Host')
    base = config.get('base', f'{proto}://{host}/')
    uri, url,rdf = f'{base}{path}',None,None

    rdf = get_resource(uri, path, base, '_reindex' not in request.args)
    context = {"@vocab": "https://schema.org/" }
    j = loads(rdf.serialize(format="json-ld", context=context).decode("utf-8"))

    j = frame_hack(j, uri)

    print(j)

    return Response(dumps(j, indent=2), mimetype='application/json') if rdf else ("Not found", 404)


def get_resource(uri, path, base, use_cache=True):
    if cache and use_cache:
        with closing(get_store()) as store:
            ctx = store.get_context(uri)
            
            if ctx:
                # There has to be a better way
                g = Graph()
                g.namespace_manager.bind('schema', URIRef('https://schema.org/'))
                for t in ctx:
                    g.add(t)

                return g
                #return Graph().parse(data=ctx.serialize())

    for u in config.get('urls', []):
        m = match(u['match'], path)

        # find target URL
        if m:
            url = u['target'].format(**m.groupdict())

            # extract RDF
            if url:
                extractor = get_extractor(u.get('mode', 'rdfa'))
                rdf = extractor(url, uri, config=u.get('config', {}), base=base)
                break

    if rdf:
        with closing(get_store()) as store:
            for t in rdf:
                store.add((t[0], t[1], t[2], uri))

    return rdf


@app.route('/favicon.ico')
def favicon():
    return 'NO!',404


def get_store():
    store = ConjunctiveGraph('Sleepycat') if config.get('store', False) else None

    if store != None:
        store.open(config['store'], create=True)

    return store


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
    ret['http://purl.org/dc/terms/relation'] = [ x for x in j['@graph'] if x['@id'] != uri ]

    return ret













