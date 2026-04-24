import datetime
import logging
from typing import Optional, Any
import xml.etree.ElementTree as ET
import uuid
import os
import yaml
from rdflib import Graph, Literal, URIRef, BNode
from rdflib.namespace import RDF, SDO, XSD
import uritools
import adlib_xpaths as xpath
import adlib_tags as tags
from adlibxml_to_schemaorg_mapping import BASIC_MAPPING, CREATOR_MAPPING, DIMENSION_MAPPING, REPRODUCTION_MAPPING, CHT_TERM_FIELDS
import adlibxml_to_schemaorg_mapping

CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
ENCODING = os.getenv('ENCODING', 'utf-8')
MODIFIED_ON_OR_AFTER = datetime.datetime.strptime(os.getenv('MODIFIED_ON_OR_AFTER', '1970-01-01'), '%Y-%m-%d')

config = yaml.safe_load(open(CONFIG_PATH, encoding=ENCODING))
logger = logging.getLogger(__name__)

def parse_tree_to_graph(target_graph: Graph, tree: Any) -> Graph:
    
    priref = get_text_from_tree(tree, xpath.PRIREF)
    cre_dt = datetime.datetime.strptime(tree.attrib['created'], '%Y-%m-%dT%H:%M:%S')
    mod_dt = datetime.datetime.strptime(tree.attrib['modification'], '%Y-%m-%dT%H:%M:%S')
    if priref and mod_dt >= MODIFIED_ON_OR_AFTER:
        record_object_node = uritools.get_object_uri(config['BASE_URI'], priref, SDO.CreativeWork)
        target_graph.add((record_object_node, SDO.sdDatePublished, Literal(mod_dt, datatype=XSD.dateTime)))
    else:
        return target_graph
    
    # adding required field isPartOf dataset reference
    target_graph.add((record_object_node, SDO.isPartOf, URIRef('https://linkeddata.cultureelerfgoed.nl/rce/datacatalog/Dataset/103')))
    for rtype in adlibxml_to_schemaorg_mapping.RECORD_OBJECT_TYPES:
        target_graph.add((record_object_node, RDF.type, rtype))

    # first degree attributes
    for key, ref in BASIC_MAPPING.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            target_graph.add((record_object_node, ref, Literal(item_text, lang='nl')))

    # first degree attributes that might be enrichable via CHT
    for key, ref in CHT_TERM_FIELDS.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            dt_url = URIRef(uritools.get_object_uri(config['BASE_URI'], str(uuid.uuid4()), SDO.DefinedTerm))
            target_graph.add((record_object_node, ref, dt_url))
            target_graph.add((dt_url, RDF.type, SDO.DefinedTerm))
            target_graph.add((dt_url, RDF.type, SDO.URL))
            target_graph.add((dt_url, SDO.name, Literal(item_text, lang='nl')))
            term_uri = uritools.get_term_uri_from_cht(item_text)
            if term_uri:
                target_graph.add((dt_url, SDO.sameAs, URIRef(term_uri)))

    # Creator
    sdo_creator_node = uritools.get_object_uri(config['BASE_URI'], priref, SDO.Person)
    target_graph.add((sdo_creator_node, RDF.type, SDO.Person))
    target_graph.add((record_object_node, SDO.creator, sdo_creator_node))
    for key, ref in CREATOR_MAPPING.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            target_graph.add((sdo_creator_node, ref[0], ref[1](item_text.strip())))

    # Link to image of object at memorix based on reproduction reference
    for index, r_ref in enumerate(tree.findall(xpath.REPRODUCTION_REFERENCE)):
        r_ref_node = uritools.get_object_uri(config['BASE_URI'], r_ref.text, REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][1])
        target_graph.add((r_ref_node, RDF.type, REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][1]))
        target_graph.add((record_object_node, REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][0], r_ref_node))
        target_graph.add((r_ref_node, REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][3], record_object_node))
        target_graph.add((r_ref_node, REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][2], uritools.get_memorix_uri_from_reference(r_ref.text)))

    # Organization 
    target_graph.add((record_object_node, SDO.provider, URIRef(config['ORG_URI'])))

    # Dimensions
    for index, dimension in enumerate(tree.findall(xpath.DIMENSION)):
        qv_node = uritools.get_object_uri(config['BASE_URI'], str(uuid.uuid4()), SDO.QuantitativeValue)
        target_graph.add((qv_node, RDF.type, SDO.QuantitativeValue))

        d_unit = next(dimension.iterfind(tags.DIMENSION_UNIT))
        if d_unit.text:
            target_graph.add((qv_node, DIMENSION_MAPPING[xpath.DIMENSION_UNIT], Literal(d_unit.text)))
        
        d_val = next(dimension.iterfind(tags.DIMENSION_VALUE))
        if d_val.text:
            target_graph.add((qv_node, DIMENSION_MAPPING[xpath.DIMENSION_VALUE], Literal(d_val.text)))
        
        d_type = next(dimension.iterfind(tags.DIMENSION_TYPE))
        if d_type.text == 'hoogte':
            target_graph.add((qv_node, SDO.valueReference, Literal('hoogte', lang='nl')))
            target_graph.add((record_object_node, SDO.height, qv_node))
        elif d_type.text == 'breedte':
            target_graph.add((qv_node, SDO.valueReference, Literal('breedte', lang='nl')))
            target_graph.add((record_object_node, SDO.width, qv_node))
        elif d_type.text == 'diepte':
            target_graph.add((qv_node, SDO.valueReference, Literal('diepte', lang='nl')))
            target_graph.add((record_object_node, SDO.depth, qv_node))

        rholder_text = get_text_from_tree(tree, xpath.RIGHTS_HOLDER)
        if rholder_text:
            sdo_rholder_node = uritools.get_object_uri(config['BASE_URI'], str(uuid.uuid4()), SDO.Person)
            target_graph.add((sdo_rholder_node, RDF.type, SDO.Person))
            target_graph.add((sdo_rholder_node, SDO.name, Literal(rholder_text)))
            target_graph.add((record_object_node, SDO.copyrightHolder, sdo_rholder_node))

    return target_graph

def get_text_from_tree(tree: (ET.ElementTree | ET.Element), target_xpath: str) -> Optional[str]:
    t_elem = tree.find(target_xpath)
    if t_elem is not None and t_elem.text:
        return t_elem.text

def make_statistics_from_string(xml: str) -> dict[str, int]:
    tree = ET.fromstring(xml)    
    return make_statistics(tree, True)

def make_statistics(tree: Any, check_text=False) -> dict[str, int]:
    stats = {
        'total_files_processed': 0
    }
    for elem in tree.iter():
        if check_text:
            text_present = (elem.text != None and elem.text.strip() != '')
            has_children = len(list(elem)) 
            if not (text_present or has_children > 0): continue
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

def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    etree = ET.parse('data/output/rubenpriref24095.adlib.xml')
    root = etree.getroot()

if __name__ == '__main__':
    main()