import logging
from rdflib import Graph
import adlib_xpaths as xpath
import adlib_tags as tags
import lod_mapper as lmap
from adlibxml_to_schemaorg_mapping import MAPPING
import adlib_transformer

logger = logging.getLogger(__name__)
path = 'data/output/rubenpriref24099.adlib.xml'


def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    parsed_record = adlib_transformer.parse_path('data/output/rubenpriref24099.adlib.xml')
    rgraph = lmap.apply_mapping(parsed_record, MAPPING)


if __name__ == '__main__':
    main()