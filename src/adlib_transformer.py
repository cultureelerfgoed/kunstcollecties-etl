from datetime import datetime
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
import adlib_xpaths as xpath
import adlib_tags as tags
import adlibxml_to_schemaorg_mapping as mapping

CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
MODIFIED_ON_OR_AFTER = datetime.strptime(os.getenv('MODIFIED_ON_OR_AFTER', '1970-01-01'), '%Y-%m-%d')

config = yaml.safe_load(open(CONFIG_PATH))
logger = logging.getLogger(__name__)

def parse_tree_to_graph(target_graph: Graph, tree: Any) -> Graph:
    """ This function takes a Graph and an XML tree and parses the tree into the graph """

    # Adlib record priref unique identifier
    priref = get_text_from_tree(tree, xpath.PRIREF)
    # Modification date of record
    mod_dt = datetime.strptime(tree.attrib['modification'], '%Y-%m-%dT%H:%M:%S')
    # Check record in scope
    if priref and mod_dt >= MODIFIED_ON_OR_AFTER:
        record_object_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], priref, SDO.CreativeWork)
        target_graph.add((record_object_node, SDO.sdDatePublished, Literal(mod_dt, datatype=XSD.dateTime)))
    else:
        return target_graph
    
    # adding required field isPartOf dataset reference
    dataset_node = uritools.get_object_uri(config['BASE_URI'], 'rce/datacatalog', 'https://kennis.cultureelerfgoed.nl/index.php/Dataset/103', SDO.Dataset)
    target_graph.add((record_object_node, SDO.isPartOf, dataset_node))

    # add record types from mapping
    for rtype in mapping.RECORD_OBJECT_TYPES:
        target_graph.add((record_object_node, RDF.type, rtype))

    # first degree attributes
    for key, ref in mapping.BASIC_MAPPING.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            target_graph.add((record_object_node, ref[0], ref[1](item_text, datatype=ref[2])))

    # add property value attributes
    for key, ref in mapping.PROPERTY_VALUE_MAPPING.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            property_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], priref, SDO.PropertyValue)
            target_graph.add((property_node, RDF.type, SDO.PropertyValue))
            target_graph.add((property_node, SDO.value, Literal(item_text, datatype=XSD.string)))
            target_graph.add((property_node, SDO.propertyID, ref[0]))
            target_graph.add((property_node, SDO.description, Literal(ref[1], datatype=XSD.string)))
            target_graph.add((record_object_node, SDO.identifier, property_node))

    # add defined terms, if configured enrich via CHT
    for key, ref in mapping.DEFINED_TERM_FIELD_MAPPING.items():
        for item in tree.findall(key):
            if item.text != None and item.text.strip() != '':
                dt_url = URIRef(uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], item.text,  mapping.DEFINED_TERM_TYPES[key][0]))
                target_graph.add((record_object_node, ref, dt_url))
                for item_type in mapping.DEFINED_TERM_TYPES[key]:
                    target_graph.add((dt_url, RDF.type, item_type))
                target_graph.add((dt_url, SDO.name, Literal(item.text, datatype=XSD.string)))
                if config['ENRICH_TERMS']:
                    term_uri = uritools.get_term_uri_from_cht(item.text)
                    if term_uri:
                        target_graph.add((dt_url, SDO.sameAs, Literal(term_uri, datatype=XSD.anyURI)))
                        logger.debug('Term URI found for %s, %s', item.text, term_uri)
                    else:
                        logger.debug('No term URI found for %s', item.text)

    # location created
    for key, ref in mapping.LOCATION_FIELDS.items():
        for item in tree.findall(key):
            if item.text != None and item.text.strip() != '':
                loc_url = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], item.text, ref[1])
                target_graph.add((loc_url, RDF.type, ref[1]))
                target_graph.add((loc_url, ref[0], Literal(item.text, lang='nl')))

    # add creator, creators are always persons in version 0.1 of datamodel
    sdo_creator_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], priref, SDO.Person)
    target_graph.add((sdo_creator_node, RDF.type, SDO.Person))
    target_graph.add((record_object_node, SDO.creator, sdo_creator_node))
    for key, ref in mapping.CREATOR_MAPPING.items():
        item_text = get_text_from_tree(tree, key)
        if item_text:
            if ref[2] == XSD.anyURI:
                # validate uri
                uri_ref = urlparse(item_text.strip())
                if (uri_ref.scheme != '' and uri_ref.netloc != ''):
                    target_graph.add((sdo_creator_node, ref[0], ref[1](item_text.strip(), datatype=ref[2])))
            else:
                target_graph.add((sdo_creator_node, ref[0], ref[1](item_text.strip(), datatype=ref[2])))

    # Link to image of object at memorix based on reproduction reference
    for index, r_ref in enumerate(tree.findall(xpath.REPRODUCTION_REFERENCE)):
        # check presence of reproduction reference and that the assigned rights permit publication 
        if r_ref.text and get_text_from_tree(tree, xpath.RIGHTS_ASSIGNED_VALUE) in config['RIGHTS_ASSIGNED_ALLOWLIST']:
            r_ref_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], r_ref.text, mapping.REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][1])
            target_graph.add((r_ref_node, RDF.type, mapping.REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][1]))
            target_graph.add((record_object_node, mapping.REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][0], r_ref_node))
            target_graph.add((r_ref_node, mapping.REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][3], record_object_node))
            target_graph.add((r_ref_node, mapping.REPRODUCTION_MAPPING[xpath.REPRODUCTION_REFERENCE][2], uritools.get_memorix_uri_from_reference(r_ref.text)))

    # Organization 
    target_graph.add((record_object_node, SDO.provider, Literal(config['ORG_URI'], datatype=XSD.anyURI)))

    # Dimensions
    for index, dimension in enumerate(tree.findall(xpath.DIMENSION)):
        qv_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], str(uuid.uuid4()), SDO.QuantitativeValue)
        target_graph.add((qv_node, RDF.type, SDO.QuantitativeValue))

        d_unit = next(dimension.iterfind(tags.DIMENSION_UNIT))
        if d_unit.text:
            target_graph.add((qv_node, mapping.DIMENSION_MAPPING[xpath.DIMENSION_UNIT], Literal(d_unit.text, datatype=XSD.string)))
        
        d_val = next(dimension.iterfind(tags.DIMENSION_VALUE))
        if d_val.text:
            target_graph.add((qv_node, mapping.DIMENSION_MAPPING[xpath.DIMENSION_VALUE], Literal(d_val.text, datatype=XSD.string)))
        
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

    # rightsholder
    rholder_text = get_text_from_tree(tree, xpath.RIGHTS_HOLDER)
    if rholder_text:
        sdo_rholder_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], str(uuid.uuid4()), SDO.Person)
        target_graph.add((sdo_rholder_node, RDF.type, SDO.Person))
        target_graph.add((sdo_rholder_node, SDO.name, Literal(rholder_text, datatype=XSD.string)))
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
