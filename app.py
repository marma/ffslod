#!/usr/bin/env python3

from flask import Flask,request,render_template,Response
from json import loads,dumps,load
from importlib import import_module
from yaml import load as yload,FullLoader
from re import match,sub
from os.path import join

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
config = yload(open(join(app.root_path, 'config.yml')).read(), Loader=FullLoader)
extractors = {}

@app.route('/favicon.ico')
def favicon():
    return 'NO!',404


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    base = config.get('base', '')
    path = f'{path}'
    host = request.headers.get('Host')
    query_string = ('?' + '&'.join([ key + '=' + value for key,value in request.args.items() ])) if request.args else ''
    uri, url,rdf = f'{base}{path}',None,None

    for u in config.get('urls', []):
        m = match(u['match'], path)
        print(u.get('config', {}))

        # find target URL
        if m:
            url = u['target'].format(**m.groupdict())

            # extract RDF
            if url:
                extractor = get_extractor(u.get('mode', 'rdfa'))
                rdf = extractor(url, uri, config=u.get('config', {}))

                #return rdf

    return Response(rdf.serialize(format="turtle").decode("utf-8"), mimetype='text/turtle') if rdf else ("Not found", 404)




def load_extractor(name):
    module = import_module(f'modules.{name}')
    f = module.extract
    #spec = spec_from_file_location(f'modules.{name}', f'modules/{name}.py')
    #exractor = importlib.util.module_from_spec(spec)
    #spec.loader.exec_module(extractor)
    #f = extractor.extract

    extractors[name] = f

    return f

def get_extractor(name):
    return extractors.get(name, load_extractor(name))
