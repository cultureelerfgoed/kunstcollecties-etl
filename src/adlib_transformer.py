import logging
from typing import Optional, Any
import xml.etree.ElementTree as ET
import uuid
from urllib.parse import urlsplit, urljoin
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SDO
import adlib_xpaths as xpath
import adlib_tags as tags
from adlibxml_to_schemaorg_mapping import BASIC_MAPPING, CREATOR_MAPPING, DIMENSION_MAPPING
import adlibxml_to_schemaorg_mapping

logger = logging.getLogger(__name__)
BASE_URI = 'https://linkeddata.cultureelerfgoed.nl/'


# https://adlibug.nl/2014/09/17/how-to-create-a-full-list-of-tags-using-xml-and-xsl/


def parse_tree_to_graph(tree: Any) -> Graph:
    sdo_record_graph = Graph()
    priref = get_text_from_tree(tree, xpath.PRIREF)
    
    if priref:
        record_object_node = get_object_uri(priref, SDO.CreativeWork)
    else:
        return sdo_record_graph
    
    for rtype in adlibxml_to_schemaorg_mapping.RECORD_OBJECT_TYPES:
        sdo_record_graph.add((record_object_node, RDF.type, rtype))

    for key, ref in BASIC_MAPPING.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            sdo_record_graph.add((record_object_node, ref, Literal(item_text, lang='nl')))

    sdo_creator_node = get_object_uri(priref, SDO.Person)
    sdo_record_graph.add((sdo_creator_node, RDF.type, SDO.Person))
    sdo_record_graph.add((record_object_node, SDO.creator, sdo_creator_node))

    for key, ref in CREATOR_MAPPING.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            sdo_record_graph.add((sdo_creator_node, ref[0], ref[1](item_text)))

    for index, dimension in enumerate(tree.findall(xpath.DIMENSION)):
        qv_node = URIRef(get_object_uri(str(uuid.uuid4()), SDO.Dimension))
        sdo_record_graph.add((qv_node, RDF.type, SDO.QuantitativeValue))

        d_unit = next(dimension.iterfind(tags.DIMENSION_UNIT))
        if d_unit.text:
            sdo_record_graph.add((qv_node, DIMENSION_MAPPING[xpath.DIMENSION_UNIT], Literal(d_unit.text)))
        
        d_val = next(dimension.iterfind(tags.DIMENSION_VALUE))
        if d_val.text:
            sdo_record_graph.add((qv_node, DIMENSION_MAPPING[xpath.DIMENSION_VALUE], Literal(d_val.text)))
        
        d_type = next(dimension.iterfind(tags.DIMENSION_TYPE))
        if d_type.text == 'hoogte':
            sdo_record_graph.add((qv_node, SDO.valueReference, Literal('hoogte', lang='nl')))
            sdo_record_graph.add((record_object_node, SDO.height, qv_node))
        elif d_type.text == 'breedte':
            sdo_record_graph.add((qv_node, SDO.valueReference, Literal('breedte', lang='nl')))
            sdo_record_graph.add((record_object_node, SDO.width, qv_node))
        elif d_type.text == 'diepte':
            sdo_record_graph.add((qv_node, SDO.valueReference, Literal('diepte', lang='nl')))
            sdo_record_graph.add((record_object_node, SDO.depth, qv_node))

        rholder_text = get_text_from_tree(tree, xpath.RIGHTS_HOLDER)
        if rholder_text:
            sdo_rholder_node = URIRef(BASE_URI+'Person/'+str(uuid.uuid4()))
            sdo_record_graph.add((sdo_rholder_node, RDF.type, SDO.Person))
            sdo_record_graph.add((sdo_rholder_node, SDO.name, Literal(rholder_text)))
            sdo_record_graph.add((record_object_node, SDO.copyrightHolder, sdo_rholder_node))

    return sdo_record_graph

def get_text_from_element(element: ET.Element, target_xpath:str) -> Optional[str]:
    target = next(element.iterfind(target_xpath))
    if target is not None and target.text and target.text.strip() != '':
        return target.text
    else:
        logger.warning('Used fallback search.')
        t_elem = element.find(target_xpath)
        if t_elem is not None and t_elem.text:
            return t_elem.text

def get_text_from_tree(tree: ET.ElementTree, target_xpath: str) -> Optional[str]:
    t_elem = tree.find(target_xpath)
    if t_elem is not None and t_elem.text:
        return t_elem.text
    
def get_object_uri(obj_id: str, obj_type=SDO.Person) -> URIRef:
    obj_pfx = ('data' + urlsplit(obj_type).path + '/')
    obj_sfx = str(uuid.uuid3(namespace=uuid.NAMESPACE_URL, name=obj_id))
    obj_ttl = urljoin(obj_pfx, obj_sfx)
    obj_uri = urljoin(BASE_URI, obj_ttl)
    return URIRef(obj_uri)

def parse_path_to_graph(path: str) -> Graph:
    tree = ET.parse(path)    
    return parse_tree_to_graph(tree)

def parse_string_to_graph(xml: str) -> Graph:
    tree = ET.fromstring(xml)    
    return parse_tree_to_graph(tree)

def make_statistics_from_string(xml: str) -> dict[str, int]:
    tree = ET.fromstring(xml)    
    return make_statistics(tree, True)

def make_statistics_from_path(path: str) -> dict[str, int]:
    tree = ET.parse(path)    
    return make_statistics(tree, True)

def make_statistics(tree: Any, check_text=False) -> dict[str, int]:
    stats = {
        'total_files_processed': 0
    }
    for elem in tree.iter():
        if check_text:
            text_present = (elem.text != None and elem.text.strip() != '')
            has_children = len(list(elem)) 
            if not (text_present or has_children): continue
        if elem.tag in stats:
            stats[elem.tag] = stats[elem.tag] + 1
        else:
            stats[elem.tag] = 1
    return stats

def combine_stats(base: dict[str, int], addition: dict[str, int]) -> dict[str, int]:
    for key in addition:
        if key in base:
            base[key] = base[key] + 1
        else:
            base[key] = 1
    return base

def print_stats(base: dict[str, int]):
    sorted_stats = dict(sorted(base.items(), key=lambda item: item[1]))
    for key in sorted_stats:
        if key == 'total_files_processed': continue
        percentage = (sorted_stats[key] / sorted_stats['total_files_processed']) * 100
        logger.info('Element %s occurred %i times (%i%%)', key, sorted_stats[key], percentage)