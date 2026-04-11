import os
import logging
from rdflib import Graph
from rdflib.namespace import SDO, RDF
import lod_mapper as lmap
from adlibxml_to_schemaorg_mapping import BASIC_MAPPING, CREATOR_MAPPING
import adlib_transformer

logger = logging.getLogger(__name__)
path = 'data/output/rubenpriref24099.adlib.xml'


def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    rgraph = Graph()

    dir_path = 'data/output/'
    limit = 100

    for index, filename in enumerate(os.listdir(dir_path)):
        if not filename.endswith('.xml'): continue
        path = os.path.join(dir_path, filename)
        parsed_record = adlib_transformer.parse_path(path)
        basic_attr = lmap.apply_mapping(parsed_record, BASIC_MAPPING)
        cw_node = basic_attr.value(None, RDF.type, SDO.CreativeWork, any=False)
        rgraph = rgraph + lmap.make_creator(parsed_record, CREATOR_MAPPING, cw_node)
        
        if index >= limit:
            break

    rgraph.print()


if __name__ == '__main__':
    main()