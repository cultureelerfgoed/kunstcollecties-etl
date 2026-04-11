import logging

from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import RDF, SDO

import adlib_xpaths

logger = logging.getLogger(__name__)

def apply_mapping(adlib_record: dict[str], mapping: dict[str]) -> Graph:
    sdo_record_graph = Graph()
    sdo_record_node = BNode()
    sdo_record_graph.add((sdo_record_node, RDF.type, SDO.CreativeWork))
    for key, val in adlib_record.items():
        if key in mapping:
            logger.info('Adding %s %s', str(mapping[key]), str(val))
            sdo_record_graph.add((sdo_record_node, mapping[key], Literal(val)))
    
    return sdo_record_graph

def make_creator(adlib_record: dict[str], mapping: dict[str]) -> Graph:
    sdo_creator_graph = Graph()
    sdo_creator_node = BNode()
    sdo_creator_graph.add((sdo_creator_node, RDF.type, SDO.Thing))

    for key, val in adlib_record.items():
        if key in mapping:
            if key == adlib_xpaths.RKDARTISTS:
                sdo_creator_graph.add((sdo_creator_node, SDO.sameAs, URIRef(adlib_record[adlib_xpaths.RKDARTISTS])))
            else:
                sdo_creator_graph.add((sdo_creator_node, mapping[key], Literal(val)))

    return sdo_creator_graph

    
