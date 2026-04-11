import logging
from rdflib import Graph
import adlib_xpaths as xpath
import adlib_tags as tags
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

    for path in ['data/output/rubenpriref24099.adlib.xml',
                 'data/output/rubenpriref158492.adlib.xml',
                 'data/output/rubenpriref158419.adlib.xml',
                 'data/output/rubenpriref158420.adlib.xml',
                 'data/output/rubenpriref158421.adlib.xml',
                 'data/output/rubenpriref158422.adlib.xml']:
        parsed_record = adlib_transformer.parse_path(path)
        rgraph = rgraph + lmap.apply_mapping(parsed_record, BASIC_MAPPING)
        rgraph = rgraph + lmap.make_creator(parsed_record, CREATOR_MAPPING)

    logger.info(rgraph.print())


if __name__ == '__main__':
    main()