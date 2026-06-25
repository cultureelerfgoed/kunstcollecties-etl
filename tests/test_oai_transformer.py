import xml.etree.ElementTree as ET
from rdflib.namespace import SDO, RDF
from rdflib import Graph
import yaml
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import transform_service
import oai_to_schemaorg_mapping as mapping
import oai_xpaths as xpath

config = yaml.safe_load(open('config/test_oai_config.yml', encoding='utf-8'))

def test_transform_valid():
    test_xml = '<record priref="98492" created="2015-04-02T02:34:13" modification="2021-07-23T06:57:15" selected="false">' \
        '<priref>98500</priref>' \
        '<object_number>aa111</object_number>' \
        '<object_category>olieverf</object_category>' \
        '<Production>' \
        '<creator>' \
        '<name>onbekend</name>' \
        '<Source><source.number>https://rkd.nl/artists/64175</source.number></Source>' \
        '</creator>' \
        '</Production>' \
        '<Rights><rights.assigned><value lang="neutral">PICTORIGHT</value><value lang="0">No, rights assigned to Pictoright</value>' \
        '<value lang="1">Nee, maar toestemming voor gebruik Pictoright (afbeelding zichtbaar) </value></rights.assigned>' \
        '<rights.holder>Gijzen, W.F.</rights.holder></Rights>' \
        '<Reproduction><reproduction.reference>37d77ebb-3c6c-d691-884e-75cdf50125f7</reproduction.reference></Reproduction>' \
        '</record>' 
    root = ET.fromstring(test_xml)
    print(f'element: {str(root.attrib)}')
    # get detailed information with priref
    graph = Graph()
    graph = transform_service.parse_tree_to_graph(graph, root, mapping, xpath)
    
    if config['ENRICH_TERMS']:
        assert len(list(graph.objects(None, SDO.sameAs))) == 2
    else:
        assert len(list(graph.objects(None, SDO.sameAs))) == 1
    assert len(list(graph.objects(None, SDO.propertyID))) == 1
    assert len(list(graph.objects(None, SDO.associatedMedia))) == 1


def test_transform_invalid():
    test_xml = '<record priref="98492" created="2015-04-02T02:34:13" modification="2021-07-23T06:57:15" selected="false">' \
        '<priref>98500</priref>' \
        '<Production>' \
        '<creator>' \
        '<name>onbekend</name>' \
        '<Source><source.number>0000 0000 8225 9251</source.number></Source>' \
        '</creator>' \
        '</Production>' \
        '</record>' 
    root = ET.fromstring(test_xml)
    # get detailed information with priref 
    graph = Graph()
    transform_service.parse_tree_to_graph(graph, root, mapping, xpath)
    assert len(list(graph.objects(None, SDO.sameAs))) == 0

def test_rights_allowlist():
    test_xml = '<record priref="98492" created="2015-04-02T02:34:13" modification="2021-07-23T06:57:15" selected="false">' \
        '<priref>98500</priref>' \
        '<object_number>aa111</object_number>' \
        '<object_category>olieverf</object_category>' \
        '<Production>' \
        '<creator>' \
        '<name>onbekend</name>' \
        '</creator>' \
        '<rkdartists>https://rkd.nl/artists/337566</rkdartists>' \
        '</Production>' \
        '<Rights><rights.assigned><value lang="neutral">NOPZB</value><value lang="0">No, publish without image</value>' \
        '<value lang="1">Nee, geen toestemming publiceren zonder beeld (afbeelding niet zichtbaar)</value>' \
        '<value lang="2">Non, publier sans image</value><value lang="3">Nein, publizieren ohne bild</value></rights.assigned>' \
        '<rights.holder>Gijzen, W.F.</rights.holder></Rights>' \
        '<Reproduction><reproduction.reference>37d77ebb-3c6c-d691-884e-75cdf50125f7</reproduction.reference></Reproduction>' \
        '</record>' 
    root = ET.fromstring(test_xml)
    # get detailed information with priref 
    graph = Graph()
    transform_service.parse_tree_to_graph(graph, root, mapping, xpath)
    assert len(list(graph.objects(None, SDO.associatedMedia))) == 0

def test_quantitative_values():
    test_xml = '<record priref="98492" created="2015-04-02T02:34:13" modification="2021-07-23T06:57:15" selected="false">' \
        '<priref>98500</priref>' \
        '<dimension.free>hoogte: 26.5 cm breedte: 40 cm</dimension.free>' \
        '<object_number>aa111</object_number>' \
        '<object_category>olieverf</object_category>' \
        '<Production>' \
        '<Dimension>' \
        '<dimension.part>Doek</dimension.part>' \
        '<dimension.type>hoogte</dimension.type>' \
        '<dimension.unit>cm</dimension.unit>' \
        '<dimension.value>146</dimension.value>' \
        '</Dimension>' \
        '<Dimension>' \
        '<dimension.part>Doek</dimension.part>' \
        '<dimension.type>breedte</dimension.type>' \
        '<dimension.unit>cm</dimension.unit>' \
        '<dimension.value>120</dimension.value>' \
        '</Dimension>' \
        '<creator>' \
        '<name>onbekend</name>' \
        '</creator>' \
        '<rkdartists>https://rkd.nl/artists/337566</rkdartists>' \
        '</Production>' \
        '<Rights><rights.assigned><value lang="neutral">NOPZB</value><value lang="0">No, publish without image</value>' \
        '<value lang="1">Nee, geen toestemming publiceren zonder beeld (afbeelding niet zichtbaar)</value>' \
        '<value lang="2">Non, publier sans image</value><value lang="3">Nein, publizieren ohne bild</value></rights.assigned>' \
        '<rights.holder>Gijzen, W.F.</rights.holder></Rights>' \
        '<Reproduction><reproduction.reference>37d77ebb-3c6c-d691-884e-75cdf50125f7</reproduction.reference></Reproduction>' \
        '</record>' 
    root = ET.fromstring(test_xml)
    # get detailed information with priref 
    graph = Graph()
    transform_service.parse_tree_to_graph(graph, root, mapping, xpath)
    assert len(list(graph.subjects(RDF.type, SDO.QuantitativeValue))) == 2

def test_place_enrichment():
    test_xml = '<record priref="98492" created="2015-04-02T02:34:13" modification="2021-07-23T06:57:15" selected="false">' \
        '<priref>98500</priref>' \
        '<dimension.free>hoogte: 26.5 cm breedte: 40 cm</dimension.free>' \
        '<object_number>aa111</object_number>' \
        '<object_category>olieverf</object_category>' \
        '<Production>' \
        '<production.place><Source><source.number>https//sws.geonames.org/2750405/</source.number></Source><term>Nederland</term></production.place>' \
        '<creator>' \
        '<name>onbekend</name>' \
        '</creator>' \
        '</Production>' \
        '</record>' 
    root = ET.fromstring(test_xml)
    # get detailed information with priref 
    graph = Graph()
    transform_service.parse_tree_to_graph(graph, root, mapping, xpath)
    assert len(list(graph.subjects(RDF.type, SDO.Place))) == 1
    assert len(list(graph.objects(None, SDO.sameAs))) == 1

def test_multiple_materials():
    test_xml = '<record priref="98492" created="2015-04-02T02:34:13" modification="2021-07-23T06:57:15" selected="false">' \
        '<priref>98500</priref>' \
        '<dimension.free>hoogte: 26.5 cm breedte: 40 cm</dimension.free>' \
        '<object_number>aa111</object_number>' \
        '<object_category>olieverf</object_category>' \
        '<Production>' \
        '<Material>' \
        '<material><term>inkt</term></material>' \
        '</Material>' \
        '<Material>' \
        '<material><term>papier</term></material>' \
        '</Material>' \
        '<creator>' \
        '<name>onbekend</name>' \
        '</creator>' \
        '</Production>' \
        '</record>' 
    root = ET.fromstring(test_xml)
    # get detailed information with priref 
    graph = Graph()
    transform_service.parse_tree_to_graph(graph, root, mapping, xpath)
    assert len(list(graph.objects(None, SDO.material))) == 2

    for s, p, o in sorted(graph):
        print(f'{s} \n {p} \n {o}')

def test_object_number_in_beeldbank():
    test_xml = '<record priref="98492" created="2015-04-02T02:34:13" modification="2021-07-23T06:57:15" selected="false">' \
        '<priref>98500</priref>' \
        '<object_number>aa111</object_number>' \
        '<object_category>olieverf</object_category>' \
        '<Production>' \
        '<creator>' \
        '<name>onbekend</name>' \
        '</creator>' \
        '<rkdartists>https://rkd.nl/artists/337566</rkdartists>' \
        '</Production>' \
        '<Rights><rights.assigned><value lang="neutral">NOPZB</value><value lang="0">No, publish without image</value>' \
        '<value lang="1">Nee, geen toestemming publiceren zonder beeld (afbeelding niet zichtbaar)</value>' \
        '<value lang="2">Non, publier sans image</value><value lang="3">Nein, publizieren ohne bild</value></rights.assigned>' \
        '<rights.holder>Gijzen, W.F.</rights.holder></Rights>' \
        '<Reproduction><reproduction.reference>37d77ebb-3c6c-d691-884e-75cdf50125f7</reproduction.reference></Reproduction>' \
        '</record>' 
    root = ET.fromstring(test_xml)
    # get detailed information with priref 
    graph = Graph()
    transform_service.parse_tree_to_graph(graph, root, mapping, xpath)
    assert len(list(graph.objects(None, SDO.url))) == 1
    url = next(graph.objects(None, SDO.url))
    assert 'beeldbank' in url
    assert 'aa111' in url 