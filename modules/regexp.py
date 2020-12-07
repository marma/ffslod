from requests import get,Session
from re import match,findall

def extract(url, uri, config={}):
    ret = [ [ uri, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', config['type'] ] ]

    # get page
    with Session() as session:
        text = session.get(url).text

        for pattern in config.get('patterns', []):
            for hit in findall(pattern['match'], text):
                ret += [ [ uri, pattern['predicate'], hit ] ]

    return str(ret)
