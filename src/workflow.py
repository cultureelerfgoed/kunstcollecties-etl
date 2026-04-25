import os
import logging
import datetime
import yaml
import uritools
import adlib_harvester

CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
ENCODING = os.getenv('ENCODING', 'utf-8')
GRAPH_ID = os.getenv('GRAPH_ID', 'default')
ARTIFACT_PATH = os.getenv('ARTIFACT_PATH', 'kc.jsonld')
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
    rgraph = uritools.get_organization(config['ORG_URI'], 
                                       config['ORG_NAME'], 
                                       config['ORG_SAME_AS'],
                                       config['ORG_CONTACT_NAME'],
                                       config['ORG_CONTACT_EMAIL'],
                                       config['ORG_ISIL'],
                                       config['ORG_ALTNAME'])

    try:
        adlib_harvester.harvest(rgraph, endpoint=config['SRC_URI'], database='ruben')
    except Exception as e:
        logger.error('Harvesting failed: %s', str(e))
    finally:
        b = datetime.datetime.now().replace(microsecond=0)
        logger.info('Finished after %s', str(b-a))
        logger.info('Writing  %s', f'{OUTPUT_FILE_FORMAT} file to {ARTIFACT_PATH}')
        rgraph.serialize(format=OUTPUT_FILE_FORMAT, 
                         destination=ARTIFACT_PATH, 
                         encoding=ENCODING, 
                         auto_compact=True,
                         )  
        logger.info("Filesize:  %s", f"{(os.path.getsize(ARTIFACT_PATH) / 1000)} KB")

if __name__ == '__main__':
    main()