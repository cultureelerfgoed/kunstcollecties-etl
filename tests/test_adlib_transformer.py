import xml.etree.ElementTree as ET
import pytest
from rdflib.namespace import SDO
from rdflib import Graph
import yaml
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import adlib_transformer

config = yaml.safe_load(open('config/config.yml', encoding='utf-8'))

def test_transform_valid():
    test_xml = '<record priref="98492" created="2015-04-02T02:34:13" modification="2021-07-23T06:57:15" selected="false">' \
                                                                                                            '<priref>98500</priref>' \
                                                                                                            '<Production>' \
                                                                                                            '<creator>' \
                                                                                                            '<name>onbekend</name>' \
                                                                                                            '</creator>' \
                                                                                                            '<rkdartists>https://rkd.nl/artists/337566</rkdartists>' \
                                                                                                            '</Production>' \
                                                                                                            '</record>' 
    root = ET.fromstring(test_xml)
    print(f'element: {str(root.attrib)}')
    # get detailed information with priref
    graph = Graph()
    graph = adlib_transformer.parse_tree_to_graph(graph, root)
    for triple in sorted(graph):
        print(triple)
    assert len(list(graph.objects(None, SDO.sameAs))) == 1


def test_transform_invalid():
    test_xml = '<record priref="98492" created="2015-04-02T02:34:13" modification="2021-07-23T06:57:15" selected="false">' \
                                                                                                            '<priref>98500</priref>' \
                                                                                                            '<Production>' \
                                                                                                            '<creator>' \
                                                                                                            '<name>onbekend</name>' \
                                                                                                            '</creator>' \
                                                                                                            '<rkdartists>0000 0000 8225 9251</rkdartists>' \
                                                                                                            '</Production>' \
                                                                                                            '</record>' 
    root = ET.fromstring(test_xml)
    # get detailed information with priref
    graph = Graph()
    adlib_transformer.parse_tree_to_graph(graph, root)
    assert len(list(graph.objects(None, SDO.sameAs))) == 0