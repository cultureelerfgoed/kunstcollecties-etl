from datetime import datetime
import logging
import re
from typing import Optional, Any
import xml.etree.ElementTree as ET
import uuid
import os
import yaml
from rdflib import Graph, Literal, Node, URIRef
from rdflib.namespace import RDF, SDO, XSD, DC
import uritools

import oai_xpaths

CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
MODIFIED_ON_OR_AFTER = datetime.strptime(os.getenv('MODIFIED_ON_OR_AFTER', '1970-01-01'), '%Y-%m-%d')

config = yaml.safe_load(open(CONFIG_PATH))
logger = logging.getLogger(__name__)

ISO_DATE = re.compile(r'^-?\d{4}(-\d{2}(-\d{2})?)?$')


def _normalize_year(value: Optional[str]) -> str:
    """'550' -> '0550': jaartallen zonder voorloopnullen zijn geen geldige ISO-8601 (en niet als jaar te lezen)."""
    value = (value or '').strip()
    return value.zfill(4) if value.isdigit() else value


def creation_dates(start: Optional[str], end: Optional[str]) -> dict:
    """Begin- en einddatum uit Adlib -> {'dateCreated': ..., 'temporal': ...}.

    CN-profiel: een enkele ISO-datum (JJJJ, JJJJ-MM, JJJJ-MM-DD) hoort in schema:dateCreated (maximaal één waarde),
    een periode in schema:temporal als ISO-interval '1888/1948'. temporal blijft altijd gevuld (zoals voorheen),
    zodat lezers van de Linked Data niets missen. Voorheen werd alleen de einddatum overgenomen en dateCreated
    nooit gevuld.
    """
    start, end = _normalize_year(start), _normalize_year(end)
    if not start and not end:
        return {'dateCreated': None, 'temporal': None}
    if not start or not end or start == end:
        value = end or start
    else:
        value = f'{start}/{end}'
    # dateCreated alleen voor een enkele ISO-datum: de SHACL van het CN-profiel staat daar geen interval toe
    # (het NDE-profiel 1.10 wel). Perioden staan in temporal.
    return {'dateCreated': value if ISO_DATE.match(value) else None, 'temporal': value}


def _qualify(target_xpath: str, ns_pfx: str) -> str:
    """'.//Production/creator/name' -> './/ns0:Production/ns0:creator/ns0:name'. Per padsegment, niet met str.replace
    (dat kon segmenten die in elkaar voorkomen onbedoeld meepakken)."""
    return '/'.join(seg if seg in ('', '.', '..') else f'{ns_pfx}:{seg}' for seg in target_xpath.split('/'))


def parse_tree_to_graph(target_graph: Graph, tree: Any, mapping: Any, xpath: Any, ns_pfx=None, ns=None, datestamp: Optional[str] = None) -> Graph:
    """ This function takes a Graph and an XML tree and parses the tree into the graph """

    # Adlib record priref unique identifier
    priref = get_text_from_tree(tree, xpath.PRIREF, ns_pfx, ns)
    # Modification date of record
    #mod_dt = datetime.strptime(tree.attrib['modification'], '%Y-%m-%dT%H:%M:%S')
    # Check record in scope
    if priref:
        record_object_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], priref, SDO.CreativeWork)
        #target_graph.add((record_object_node, SDO.sdDatePublished, Literal(mod_dt, datatype=XSD.dateTime)))
    else:
        logger.warning('no priref found skipping record')
        return target_graph
    
    # adding required field isPartOf dataset reference
    # dataset_node = uritools.get_object_uri(config['BASE_URI'], 'rce/datacatalog', 'https://kennis.cultureelerfgoed.nl/index.php/Dataset/103', SDO.Dataset)
    dataset_node = URIRef('https://linkeddata.cultureelerfgoed.nl/rce/rijkscollectie-rce/')
    target_graph.add((record_object_node, SDO.isPartOf, dataset_node))

    # add record types from mapping
    for rtype in mapping.RECORD_OBJECT_TYPES:
        target_graph.add((record_object_node, RDF.type, rtype))

    # first degree attributes
    for key, ref in mapping.CREATIVEWORK_MAPPING.items():
        item_text = get_text_from_tree(tree, ref, ns_pfx, ns)
        if item_text:
            target_graph.add((record_object_node, key, Literal(item_text, lang='nl')))

    # add property value attributes
    for key, ref in mapping.PROPERTY_VALUE_MAPPING.items():
        item_text = get_text_from_tree(tree, key, ns_pfx, ns)
        if item_text:
            property_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], f'{priref}/{key}', SDO.PropertyValue)
            target_graph.add((property_node, RDF.type, SDO.PropertyValue))
            target_graph.add((property_node, SDO.value, Literal(item_text, datatype=XSD.string)))
            target_graph.add((property_node, SDO.propertyID, ref[1]))
            target_graph.add((property_node, SDO.description, Literal(ref[2], datatype=XSD.string)))
            target_graph.add((record_object_node, ref[0], property_node))

            if key == xpath.OBJECT_NUMBER:
                target_graph.add((record_object_node, SDO.url, uritools.get_beeldbank_result_from_adlib_object_number(item_text)))

    # add defined terms
    process_defined_terms(target_graph, tree, record_object_node, mapping.DEFINED_TERM_FIELD_MAPPING, mapping.DEFINED_TERM_TYPES, ns_pfx, ns)

    # datering: dateCreated (ISO-datum) en/of temporal (ook perioden), uit begin- en einddatum
    dates = creation_dates(get_text_from_tree(tree, xpath.PRODUCTION_DATE_START, ns_pfx, ns),
                           get_text_from_tree(tree, xpath.PRODUCTION_DATE_END, ns_pfx, ns))
    if dates['dateCreated']:
        target_graph.add((record_object_node, SDO.dateCreated, Literal(dates['dateCreated'], datatype=XSD.string)))
    if dates['temporal']:
        target_graph.add((record_object_node, SDO.temporal, Literal(dates['temporal'], lang='nl')))

    # opschriften en signaturen -> schema:text (NDE-profiel: getranscribeerde tekst op het object)
    for ins in findall_ns_wrapper(tree, xpath.INSCRIPTION_DESCRIPTION, ns_pfx, ns):
        if ins.text and ins.text.strip():
            target_graph.add((record_object_node, SDO.text, Literal(ins.text.strip(), lang='nl')))

    # datum waarop het record in de bron voor het laatst is gewijzigd (verplicht in het CN-profiel)
    if datestamp:
        target_graph.add((record_object_node, SDO.sdDatePublished, Literal(datestamp[:10], datatype=XSD.date)))

    # add creators: één Person per Production-groep. Een record kan meerdere makers hebben; elke maker neemt
    # alleen de gegevens uit zijn eigen groep mee (voorheen: find() over het hele record, dus alleen de eerste
    # maker, en rol/datums/RKD van latere makers werden aan die eerste maker gehangen).
    for index, group in enumerate(findall_ns_wrapper(tree, xpath.PRODUCTION, ns_pfx, ns)):
        creator_name = get_text_from_tree(group, xpath.GROUP_CREATOR_NAME, ns_pfx, ns)
        if not creator_name or not creator_name.strip():
            continue  # groep zonder maker: geen (naamloze, willekeurige) Person aanmaken
        creator_priref = get_text_from_tree(group, xpath.GROUP_CREATOR_PRIREF, ns_pfx, ns)
        # Vaste sleutel: zelfde priref -> zelfde adres; zonder priref afgeleid van record en positie (nooit willekeurig)
        creator_key = creator_priref.strip() if creator_priref else f'{priref}/creator/{index}'
        sdo_creator_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], creator_key, SDO.Person)
        target_graph.add((sdo_creator_node, RDF.type, SDO.Person))
        target_graph.add((record_object_node, SDO.creator, sdo_creator_node))

        for key, ref in mapping.CREATOR_MAPPING.items():
            item_text = get_text_from_tree(group, ref[0], ns_pfx, ns)
            if item_text and item_text.strip():
                if ref[1] == URIRef and uritools.is_valid_uri(item_text.strip()):
                    target_graph.add((sdo_creator_node, key, ref[1](item_text.strip())))
                elif ref[1] == Literal and ref[2]:
                    target_graph.add((sdo_creator_node, key, ref[1](item_text.strip(), datatype=ref[2])))
                elif ref[1] == Literal:
                    target_graph.add((sdo_creator_node, key, ref[1](item_text.strip())))

        process_defined_terms(target_graph, group, sdo_creator_node, mapping.CREATOR_DEFINED_TERM_MAPPING, mapping.CREATOR_DEFINED_TERM_TYPES, ns_pfx, ns)

    # thema's -> schema:about
    for about_path in mapping.ABOUT_TERM_PATHS:
        for about_el in findall_ns_wrapper(tree, about_path, ns_pfx, ns):
            about_name = (about_el.text or '').strip()
            if about_name:
                about_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], about_name, SDO.DefinedTerm)
                target_graph.add((about_node, RDF.type, SDO.DefinedTerm))
                target_graph.add((about_node, SDO.name, Literal(about_name, datatype=XSD.string)))
                target_graph.add((record_object_node, SDO.about, about_node))

    # overige nummers (inventarisnummer, plaatsingsnummer, ...) -> identifier (PropertyValue, zoals object_number)
    for index, alt in enumerate(findall_ns_wrapper(tree, xpath.ALTERNATIVE_NUMBER, ns_pfx, ns)):
        alt_value = get_text_from_tree(alt, xpath.ALTERNATIVE_NUMBER_VALUE, ns_pfx, ns)
        if alt_value and alt_value.strip():
            alt_type = get_text_from_tree(alt, xpath.ALTERNATIVE_NUMBER_TYPE, ns_pfx, ns)
            alt_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], f'{priref}/alternative_number/{index}', SDO.PropertyValue)
            target_graph.add((alt_node, RDF.type, SDO.PropertyValue))
            target_graph.add((alt_node, SDO.value, Literal(alt_value.strip(), datatype=XSD.string)))
            target_graph.add((alt_node, SDO.description, Literal((alt_type or 'alternative_number').strip(), datatype=XSD.string)))
            target_graph.add((record_object_node, SDO.identifier, alt_node))

    # Link to image of object at memorix based on reproduction reference
    repro_list = findall_ns_wrapper(tree, mapping.MEDIAOBJECT_MAPPING[SDO.contentUrl], ns_pfx, ns)
    if repro_list:
        for index, r_ref in enumerate(repro_list):
            # check presence of reproduction reference and that the assigned rights permit publication 
            if r_ref.text and get_text_from_tree(tree, xpath.RIGHTS_ASSIGNED_VALUE, ns_pfx, ns) in config['RIGHTS_ASSIGNED_ALLOWLIST']:
                r_ref_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], r_ref.text, mapping.MEDIAOBJECT_MAPPING[RDF.type])
                target_graph.add((r_ref_node, RDF.type, mapping.MEDIAOBJECT_MAPPING[RDF.type]))
                target_graph.add((record_object_node, SDO.associatedMedia, r_ref_node))
                target_graph.add((r_ref_node, SDO.encodesCreativeWork, record_object_node))
                target_graph.add((r_ref_node, SDO.contentUrl, uritools.get_memorix_uri_from_reference(r_ref.text)))
                target_graph.add((r_ref_node, SDO.license, mapping.MEDIAOBJECT_MAPPING[SDO.license]))
                target_graph.add((r_ref_node, SDO.thumbnailUrl, uritools.get_memorix_uri_from_reference(r_ref.text, size='200x200')))


    # Dimensions
    qv_list = findall_ns_wrapper(tree, xpath.DIMENSION, ns_pfx, ns)
    for qv_index, qv_dimension in enumerate(qv_list):
        qv_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], f'{priref}/dimension/{qv_index}', SDO.QuantitativeValue)
        
        try:
            d_unit = get_text_from_tree(qv_dimension, xpath.DIMENSION_UNIT, ns_pfx, ns)
            target_graph.add((qv_node, RDF.type, SDO.QuantitativeValue))
            if d_unit:
                target_graph.add((qv_node, mapping.DIMENSION_MAPPING[xpath.DIMENSION_UNIT], Literal(d_unit, datatype=XSD.string)))
            
            #d_val = next(dimension.iterfind(tags.DIMENSION_VALUE))
            d_val = get_text_from_tree(qv_dimension, xpath.DIMENSION_VALUE, ns_pfx, ns)
            if d_val:
                target_graph.add((qv_node, mapping.DIMENSION_MAPPING[xpath.DIMENSION_VALUE], Literal(d_val, datatype=XSD.string)))
            
            #d_type = next(dimension.iterfind(tags.DIMENSION_TYPE))
            d_type = get_text_from_tree(qv_dimension, xpath.DIMENSION_TYPE, ns_pfx, ns)
            target_graph.add((qv_node, SDO.valueReference, Literal(d_type, lang='nl')))
            target_graph.add((record_object_node, SDO.size, qv_node))
        except StopIteration:
            logger.error('Invalid Dimension: %s', ET.tostring(qv_dimension))
            target_graph.remove((qv_node, None, None))
            target_graph.remove((None, None, qv_node))        

    # rightsholder
    rholder_text = get_text_from_tree(tree, xpath.RIGHTS_HOLDER, ns_pfx, ns)
    if rholder_text:
        # gedeeld per naam (zoals termen), maar los van makers die op priref worden geadresseerd
        sdo_rholder_node = uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], f'rightsholder/{rholder_text.strip()}', SDO.Person)
        target_graph.add((sdo_rholder_node, RDF.type, SDO.Person))
        target_graph.add((sdo_rholder_node, SDO.name, Literal(rholder_text, datatype=XSD.string)))
        target_graph.add((record_object_node, SDO.copyrightHolder, sdo_rholder_node))

    return target_graph
    
def get_text_from_tree(tree: (ET.ElementTree | ET.Element), target_xpath: str, ns_pfx: Optional[str], ns: Optional[str]) -> Optional[str]:
    if ns_pfx and ns:
        t_elem = tree.find(_qualify(target_xpath, ns_pfx), namespaces={ns_pfx:ns})
    else:
        t_elem = tree.find(target_xpath)
    if t_elem is not None and t_elem.text:
        return t_elem.text
    
def findall_ns_wrapper(tree: (ET.ElementTree | ET.Element), target_xpath: str, ns_pfx: Optional[str], ns: Optional[str]) -> Optional[list[ET.Element]]:
    if ns_pfx and ns:
        t_elems = tree.findall(_qualify(target_xpath, ns_pfx), namespaces={ns_pfx:ns})
    else:
        t_elems = tree.findall(target_xpath)
    return t_elems

def process_defined_terms(target_graph: Graph, tree: (ET.ElementTree | ET.Element), target_node: Node, field_mapping: dict[str|list], type_mapping: dict[str|list], ns_pfx: Optional[str], ns: Optional[str]):
    # add defined terms
    for key, ref in field_mapping.items():
        for dt_item in findall_ns_wrapper(tree, key, ns_pfx, ns):
            
            if ref[1]:
                dt_name = get_text_from_tree(dt_item, ref[1], ns_pfx, ns)
            else:
                dt_name = get_text_from_tree(tree, key, ns_pfx, ns)

            if dt_name:
                dt_url = URIRef(uritools.get_object_uri(config['BASE_URI'], config['COLLECTION_ID'], dt_name,  type_mapping[key][0]))
                
                target_graph.add((target_node, ref[0], dt_url))
                target_graph.add((dt_url, SDO.name, Literal(dt_name, datatype=XSD.string)))
                for item_type in type_mapping[key]:
                    target_graph.add((dt_url, RDF.type, item_type))

                dt_same_as = get_text_from_tree(dt_item, ref[2], ns_pfx, ns)
                if dt_same_as and uritools.is_valid_uri(dt_same_as):
                    target_graph.add((dt_url, SDO.sameAs, URIRef(dt_same_as)))

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