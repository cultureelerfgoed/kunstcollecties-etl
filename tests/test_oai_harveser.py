import xml.etree.ElementTree as ET
import pytest
from rdflib.namespace import SDO, RDF
from rdflib import Graph
import yaml
import sys
import os
#sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import src.oai_harvester

config = yaml.safe_load(open('config/config.yml', encoding='utf-8'))

def test_harvest():
    t_graph = Graph()
    oai_harvester.harvest(t_graph, endpoint=config['SRC_URI'], db=config['SRC_DB'])