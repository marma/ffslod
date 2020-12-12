#!/usr/bin/env python3

from flask import Flask,request,render_template,Response
from rdflib import ConjunctiveGraph
from json import loads,dumps,load
from importlib import import_module
from yaml import load as yload,FullLoader
from re import match,sub
from os.path import join
from contextlib import closing

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
config = yload(open(join(app.root_path, 'config.yml')).read(), Loader=FullLoader)
extractors = {}
cache = config.get('cache', False)

@app.route('/', defaults={ 'path': '' })
@app.route('/<path:path>')
def catch_all(path):
    base = config.get('base', '')
    path = f'{path}'
    host = request.headers.get('Host')
    query_string = ('?' + '&'.join([ key + '=' + value for key,value in request.args.items() ])) if request.args else ''
    uri, url,rdf = f'{base}{path}',None,None

    if cache and not request.args.get('_reindex', False):
        with closing(get_store()) as store:
            ctx = store.get_context(uri)
            
            if ctx:
                return Response(ctx.serialize(format="turtle").decode("utf-8"), mimetype='text/turtle')

    for u in config.get('urls', []):
        m = match(u['match'], path)

        # find target URL
        if m:
            url = u['target'].format(**m.groupdict())

            # extract RDF
            if url:
                extractor = get_extractor(u.get('mode', 'rdfa'))
                rdf = extractor(url, uri, config=u.get('config', {}))
                break

    if rdf:
        with closing(get_store()) as store:
            for t in rdf:
                store.add((t[0], t[1], t[2], uri))

    return Response(rdf.serialize(format="turtle").decode("utf-8"), mimetype='text/turtle') if rdf else ("Not found", 404)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/_sparql')
def sparql():
    return render_template('sparql.html')


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
