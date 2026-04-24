import os
import logging
import datetime
from rdflib import Graph
from rdflib.namespace import SDO, RDF, RDFS
import yaml
import adlib_harvester
import adlib_transformer

CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
ENCODING = os.getenv('ENCODING', 'utf-8')
GRAPH_ID = os.getenv('GRAPH_ID', 'default')
ARTIFACT_PATH = os.getenv('ARTIFACT_PATH', 'kc.trig')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'trig')

config = yaml.safe_load(open(CONFIG_PATH, encoding=ENCODING))
logger = logging.getLogger(__name__)

def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    a = datetime.datetime.now().replace(microsecond=0)
    rgraph = Graph()
    rgraph.bind('sdo', SDO, override=True)
    rgraph.bind('rdf', RDF, override=True)
    rgraph.bind('rdfs', RDFS, override=True)
    adlib_transformer.add_organization(rgraph)

    try:
        adlib_harvester.harvest(rgraph, endpoint=config['SRC_URI'], database='ruben', make_stats=False)
    except Exception as e:
        logger.warning('Generic Exception: %s', str(e))
    finally:
        b = datetime.datetime.now().replace(microsecond=0)
        logger.info('Finished after %s', str(b-a))
        logger.info('Writing  %s', f'{OUTPUT_FILE_FORMAT} file to {ARTIFACT_PATH}')
        rgraph.serialize(format=OUTPUT_FILE_FORMAT, 
                         destination=ARTIFACT_PATH, 
                         encoding=ENCODING, 
                         auto_compact=True,
                         context={'sdo': SDO._NS,
                                  'rdf': RDF._NS,
                                  'rdfs': RDFS._NS,},
                         )  
        logger.info("Filesize:  %s", f"{(os.path.getsize(ARTIFACT_PATH) / 1000)} KB")

if __name__ == '__main__':
    main()