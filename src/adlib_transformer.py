import datetime
import logging
from typing import Optional, Any
import xml.etree.ElementTree as ET
import uuid
import os
from urllib.parse import urlparse
import yaml
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SDO, XSD
import uritools
from CHTService import CHTService
import adlib_xpaths as xpath
import adlib_tags as tags
import adlibxml_to_schemaorg_mapping as mapping

CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
ENCODING = os.getenv('ENCODING', 'utf-8')
MODIFIED_ON_OR_AFTER = datetime.datetime.strptime(os.getenv('MODIFIED_ON_OR_AFTER', '1970-01-01'), '%Y-%m-%d')

config = yaml.safe_load(open(CONFIG_PATH, encoding=ENCODING))
logger = logging.getLogger(__name__)

def parse_tree_to_graph(target_graph: Graph, tree: Any) -> Graph:
    
    priref = get_text_from_tree(tree, xpath.PRIREF)
    mod_dt = datetime.datetime.strptime(tree.attrib['modification'], '%Y-%m-%dT%H:%M:%S')
    if priref and mod_dt >= MODIFIED_ON_OR_AFTER:
        record_object_node = uritools.get_object_uri(config['BASE_URI'], priref, config['COLLECTION_ID'], SDO.CreativeWork)
        target_graph.add((record_object_node, SDO.sdDatePublished, Literal(mod_dt, datatype=XSD.dateTime)))
    else:
        return target_graph
    
    # adding required field isPartOf dataset reference
    target_graph.add((record_object_node, SDO.isPartOf, URIRef('https://linkeddata.cultureelerfgoed.nl/rce/datacatalog/Dataset/103')))
    for rtype in mapping.RECORD_OBJECT_TYPES:
        target_graph.add((record_object_node, RDF.type, rtype))

    # first degree attributes with language tag 'nl'
    for key, ref in mapping.BASIC_MAPPING_NL.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            target_graph.add((record_object_node, ref, Literal(item_text, lang='nl')))

    # first degree attributes
    for key, ref in mapping.BASIC_MAPPING.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            target_graph.add((record_object_node, ref, Literal(item_text)))

    # defined terms that might be enrichable via CHT
    for key, ref in mapping.CHT_TERM_FIELD_MAPPING.items():
        for item in tree.findall(key):
            if item.text != None and item.text.strip() != '':
                dt_url = URIRef(uritools.get_object_uri(config['BASE_URI'], item.text, config['COLLECTION_ID'], mapping.CHT_TERM_TYPES[key][0]))
                target_graph.add((record_object_node, ref, dt_url))
                for item_type in mapping.CHT_TERM_TYPES[key]:
                    target_graph.add((dt_url, RDF.type, item_type))
                target_graph.add((dt_url, SDO.name, Literal(item.text, lang='nl')))
                if config['ENRICH_TERMS']:
                    cht = CHTService()
                    term_uri = cht.get_term(item.text)
                    if term_uri:
                        target_graph.add((dt_url, SDO.sameAs, URIRef(term_uri)))

    # location created
    for key, ref in mapping.LOCATION_FIELDS.items():
        for item in tree.findall(key):
            if item.text != None and item.text.strip() != '':
                loc_url = URIRef(uritools.get_object_uri(config['BASE_URI'], item.text, config['COLLECTION_ID'], ref[1]))
                target_graph.add((loc_url, RDF.type, ref[1]))
                target_graph.add((loc_url, ref[0], Literal(item.text, lang='nl')))

    # Creator
    sdo_creator_node = uritools.get_object_uri(config['BASE_URI'], priref, config['COLLECTION_ID'], SDO.Person)
    target_graph.add((sdo_creator_node, RDF.type, SDO.Person))
    target_graph.add((record_object_node, SDO.creator, sdo_creator_node))
    for key, ref in mapping.CREATOR_MAPPING.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            if ref[1] == URIRef:
                # validate uri
                uri_ref = urlparse(item_text.strip())
                if (uri_ref.scheme != '' and uri_ref.netloc != ''):
                    target_graph.add((sdo_creator_node, ref[0], ref[1](item_text.strip())))
            else:
                target_graph.add((sdo_creator_node, ref[0], ref[1](item_text.strip())))

    # Link to image of object at memorix based on reproduction reference
    for index, r_ref in enumerate(tree.findall(xpath.REPRODUCTION_REFERENCE)):
        if r_ref.text:
            r_ref_node = uritools.get_object_uri(config['BASE_URI'], r_ref.text, config['COLLECTION_ID'], mapping.REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][1])
            target_graph.add((r_ref_node, RDF.type, mapping.REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][1]))
            target_graph.add((record_object_node, mapping.REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][0], r_ref_node))
            target_graph.add((r_ref_node, mapping.REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][3], record_object_node))
            target_graph.add((r_ref_node, mapping.REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][2], uritools.get_memorix_uri_from_reference(r_ref.text)))

    # Organization 
    target_graph.add((record_object_node, SDO.provider, URIRef(config['ORG_URI'])))

    # Dimensions
    for index, dimension in enumerate(tree.findall(xpath.DIMENSION)):
        qv_node = uritools.get_object_uri(config['BASE_URI'], str(uuid.uuid4()), config['COLLECTION_ID'], SDO.QuantitativeValue)
        target_graph.add((qv_node, RDF.type, SDO.QuantitativeValue))

        d_unit = next(dimension.iterfind(tags.DIMENSION_UNIT))
        if d_unit.text:
            target_graph.add((qv_node, mapping.DIMENSION_MAPPING[xpath.DIMENSION_UNIT], Literal(d_unit.text)))
        
        d_val = next(dimension.iterfind(tags.DIMENSION_VALUE))
        if d_val.text:
            target_graph.add((qv_node, mapping.DIMENSION_MAPPING[xpath.DIMENSION_VALUE], Literal(d_val.text)))
        
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
            sdo_rholder_node = uritools.get_object_uri(config['BASE_URI'], str(uuid.uuid4()), config['COLLECTION_ID'], SDO.Person)
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
