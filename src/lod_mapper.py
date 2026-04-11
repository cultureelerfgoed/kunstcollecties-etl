import uuid
import logging

from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import RDF, SDO

import adlib_xpaths

logger = logging.getLogger(__name__)
BASE_URI = 'https://linkeddata.cultureelerfgoed.nl/data/'

def apply_mapping(adlib_record: dict[str], mapping: dict[str]) -> Graph:
    sdo_record_graph = Graph()
    sdo_record_node = URIRef(BASE_URI+'CreativeWork/'+str(uuid.uuid4()))
    sdo_record_graph.add((sdo_record_node, RDF.type, SDO.CreativeWork))
    logger.info('adding cw: %s', str(sdo_record_node))
    for key, val in adlib_record.items():
        if key in mapping:
            logger.info('Adding %s %s', str(mapping[key]), str(val))
            sdo_record_graph.add((sdo_record_node, mapping[key], Literal(val)))
    
    return sdo_record_graph

def make_creator(adlib_record: dict[str], mapping: dict[str], creative_work: URIRef) -> Graph:
    logger.info('Creating creator for %s', str(creative_work))
    sdo_creator_graph = Graph()
    sdo_creator_node = URIRef(BASE_URI+'Thing/'+str(uuid.uuid4()))
    sdo_creator_graph.add((sdo_creator_node, RDF.type, SDO.Thing))
    sdo_creator_graph.add((creative_work, SDO.creator, sdo_creator_node))

    for key, val in adlib_record.items():
        if key in mapping:
            if key == adlib_xpaths.RKDARTISTS:
                sdo_creator_graph.add((sdo_creator_node, SDO.sameAs, URIRef(adlib_record[adlib_xpaths.RKDARTISTS])))
            else:
                sdo_creator_graph.add((sdo_creator_node, mapping[key], Literal(val)))

    return sdo_creator_graph

    
