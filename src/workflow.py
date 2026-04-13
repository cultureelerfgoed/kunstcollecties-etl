import os
import logging
import datetime
from rdflib import Graph
import adlib_transformer
import adlib_harvester

logger = logging.getLogger(__name__)
path = 'data/output/'

GRAPH_ID = os.getenv('GRAPH_ID', 'default')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'kc.jsonld')
ENCODING = os.getenv('ENCODING', 'utf-8')

def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    a = datetime.datetime.now().replace(microsecond=0)
    rgraph = Graph()
    try:
        rgraph = adlib_harvester.harvest(endpoint='https://rcerijswijk.adlibhosting.com/api.wo2/wwwopac.ashx', database='ruben', test=True)
    except OSError as oe:
        logger.warning('Failed to write to file: %s', oe)
    except TypeError as te:
        logger.warning('Failed to find an element: %s', te)
    finally:
        b = datetime.datetime.now().replace(microsecond=0)
        logger.info('Finished after %s', str(b-a))
        logger.info("Writing  %s", f"{OUTPUT_FILE_FORMAT} file to {TARGET_FILEPATH}")
        rgraph.serialize(format=OUTPUT_FILE_FORMAT, destination=TARGET_FILEPATH, encoding=ENCODING, auto_compact=True)  
        logger.info("Filesize:  %s", f"{os.path.getsize(TARGET_FILEPATH)} bytes")

if __name__ == '__main__':
    main()