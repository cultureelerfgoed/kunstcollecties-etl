import os
from typing import Optional
import uritools
import yaml
from rdflib import Graph, Literal
from rdflib.namespace import SKOS
from singleton_decorator import singleton

CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
ENCODING = os.getenv('ENCODING', 'utf-8')

config = yaml.safe_load(open(CONFIG_PATH, encoding=ENCODING))

@singleton
class CHTService:
    """ A wrapper class for CHT caching """
    cht_graph = Graph()

    def __init__(self):
        if not config['USE_CHT_API']:
            self.cht_graph = Graph()
            self.cht_graph.parse('cht.trig')

    def get_term(self, term: str) -> Optional[str]:
        if config['USE_CHT_API']:
            return uritools.get_term_uri_from_cht(term)
        else:
            r_list = list()
            r_list.extend(self.cht_graph.subjects(SKOS.prefLabel, Literal(term, lang='nl')))
            r_list.extend(self.cht_graph.subjects(SKOS.altLabel, Literal(term, lang='nl')))
            return next(iter(r_list), None)
