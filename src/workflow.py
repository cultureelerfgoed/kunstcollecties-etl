import os
import logging
from rdflib import Graph
import adlib_transformer

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
    
    limit = 100
    rgraph = Graph()
    
    try:
        for index, filename in enumerate(os.listdir(path)):
            if not filename.endswith('.xml'): continue
            fpath = os.path.join(path, filename)
            rgraph = rgraph +  adlib_transformer.parse_path_to_graph(fpath)
            
            if index >= limit:
                break
    except OSError as oe:
            logger.warning('Failed to write to file: %s', oe)
    finally:
        logger.info("Writing  %s", f"{OUTPUT_FILE_FORMAT} file to {TARGET_FILEPATH}")
        rgraph.serialize(format=OUTPUT_FILE_FORMAT, destination=TARGET_FILEPATH, encoding=ENCODING, auto_compact=True)  
        logger.info("Filesize:  %s", f"{os.path.getsize(TARGET_FILEPATH)} bytes")

if __name__ == '__main__':
    main()