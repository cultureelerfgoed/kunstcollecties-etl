import os
import logging
import datetime
from rdflib import Graph
import yaml
import adlib_harvester

CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
ENCODING = os.getenv('ENCODING', 'utf-8')
GRAPH_ID = os.getenv('GRAPH_ID', 'default')
ARTIFACT_PATH = os.getenv('ARTIFACT_PATH', 'kc.json-ld')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')

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
    try:
        rgraph = adlib_harvester.harvest(endpoint=config['SRC_URI'], database='ruben', test=True)
    except OSError as oe:
        logger.warning('Failed to write to file: %s', oe)
    except TypeError as te:
        logger.warning('TypeError: %s', te)
    finally:
        b = datetime.datetime.now().replace(microsecond=0)
        logger.info('Finished after %s', str(b-a))
        logger.info("Writing  %s", f"{OUTPUT_FILE_FORMAT} file to {ARTIFACT_PATH}")
        rgraph.serialize(format=OUTPUT_FILE_FORMAT, destination=ARTIFACT_PATH, encoding=ENCODING, auto_compact=True)  
        logger.info("Filesize:  %s", f"{os.path.getsize(ARTIFACT_PATH)} bytes")

if __name__ == '__main__':
    main()