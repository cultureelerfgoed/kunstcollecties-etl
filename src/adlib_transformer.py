import logging
import xml.etree.ElementTree as ET
import adlib_xpaths as xpath
import adlib_tags as tags
import lod_mapper as lmap
import uuid
from rdflib import Graph
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SDO
from adlibxml_to_schemaorg_mapping import BASIC_MAPPING, CREATOR_MAPPING, DIMENSION_MAPPING

logger = logging.getLogger(__name__)
BASE_URI = 'https://linkeddata.cultureelerfgoed.nl/data/'


# https://adlibug.nl/2014/09/17/how-to-create-a-full-list-of-tags-using-xml-and-xsl/

def get_tree_text_from_xpath_safe(tree: ET, target_xpath: str) -> str:
    t_elem = tree.find(target_xpath)
    if t_elem is not None and t_elem.text:
        return t_elem.text

def get_element_text_from_xpath_safe(element: ET.Element, target_xpath: str) -> str:
    t_elem = element.find(target_xpath)
    if t_elem is not None and t_elem.text:
        return t_elem.text

def parse_tree_to_graph(tree: ET) -> Graph:
    sdo_record_graph = Graph()
    cwork_node = URIRef(BASE_URI+'CreativeWork/'+str(uuid.uuid4()))
    sdo_record_graph.add((cwork_node, RDF.type, SDO.CreativeWork))

    for key, ref in BASIC_MAPPING.items():
        item_text = get_tree_text_from_xpath_safe(tree, key)
        if item_text:
            sdo_record_graph.add((cwork_node, ref, Literal(item_text)))

    sdo_creator_node = URIRef(BASE_URI+'Thing/'+str(uuid.uuid4()))
    sdo_record_graph.add((sdo_creator_node, RDF.type, SDO.Thing))
    sdo_record_graph.add((cwork_node, SDO.creator, sdo_creator_node))

    for key, ref in CREATOR_MAPPING.items():
        item_text = get_tree_text_from_xpath_safe(tree, key)
        if item_text:
            if key == xpath.RKDARTISTS:
                sdo_record_graph.add((sdo_creator_node, ref, URIRef(item_text)))
            else:
                sdo_record_graph.add((cwork_node, ref, Literal(item_text)))

    for index, dimension in enumerate(tree.findall(xpath.DIMENSION)):
        qv_node = URIRef(BASE_URI+'QuantitativeValue/'+str(uuid.uuid4()))
        sdo_record_graph.add((qv_node, RDF.type, SDO.QuantitativeValue))

        d_unit = next(dimension.iterfind(tags.DIMENSION_UNIT))
        if d_unit.text:
            sdo_record_graph.add((qv_node, DIMENSION_MAPPING[xpath.DIMENSION_UNIT], Literal(d_unit.text)))
        
        d_val = next(dimension.iterfind(tags.DIMENSION_VALUE))
        if d_val.text:
            sdo_record_graph.add((qv_node, DIMENSION_MAPPING[xpath.DIMENSION_VALUE], Literal(d_val.text)))
        
        d_type = next(dimension.iterfind(tags.DIMENSION_TYPE))
        if d_type.text == 'hoogte':
            sdo_record_graph.add((cwork_node, SDO.height, qv_node))
        elif d_type.text == 'breedte':
            sdo_record_graph.add((cwork_node, SDO.width, qv_node))
        elif d_type.text == 'diepte':
            sdo_record_graph.add((cwork_node, SDO.depth, qv_node))

    return sdo_record_graph

def parse_path_to_graph(path: str) -> Graph:
    graph = ET.parse(path)    
    return parse_tree_to_graph(graph)