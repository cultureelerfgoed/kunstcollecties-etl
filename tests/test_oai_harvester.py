import logging
from rdflib.namespace import SDO, RDF
from rdflib import Graph
import yaml
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import oai_harvester
import uritools

config = yaml.safe_load(open('config/config.yml', encoding='utf-8'))
logger = logging.getLogger(__name__)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

def test_harvest():
    print('Starting harvest test.')
    rgraph = uritools.get_organization(config['ORG_URI'], 
                                        config['ORG_NAME'], 
                                        config['ORG_SAME_AS'],
                                        config['ORG_CONTACT_NAME'],
                                        config['ORG_CONTACT_EMAIL'],
                                        config['ORG_ISIL'],
                                        config['ORG_ALTNAME'])
    print('Calling harvester..')
    rgraph = oai_harvester.harvest(rgraph, 
                        base_url=config['SRC_URI'], 
                        verb='ListRecords', 
                        metadata_prefix='rs', 
                        set_spec=config['SRC_DB'],
                        max_items=100,
                        start_from=3000)
    records = len(list(rgraph.subjects(RDF.type, SDO.ArchiveComponent)))
    assert records == 100
    