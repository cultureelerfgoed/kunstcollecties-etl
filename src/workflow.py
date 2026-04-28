import os
import logging
import datetime
import argparse
import yaml
import uritools
from rdflib.namespace import SDO, RDF
import adlib_harvester

def main():
    """ main runner for workflow """

    CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
    ENCODING = os.getenv('ENCODING', 'utf-8')
    ARTIFACT_PATH = os.getenv('ARTIFACT_PATH', 'kc.jsonld')
    OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
    START_FROM = int(os.getenv('START_FROM', '0'))
    END_AT = int(os.getenv('START_FROM', '200000'))

    config = yaml.safe_load(open(CONFIG_PATH, encoding=ENCODING))
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    parser = argparse.ArgumentParser("Kunstcollecties ETL")
    parser.add_argument("--out", help="Path for output", type=str)
    parser.add_argument("-s", help="Record number to start harvest from", type=int)
    parser.add_argument("-e", help="Record number to end harvest at", type=int)

    args = parser.parse_args()
    if args.out:
        ARTIFACT_PATH = args.out
    if args.s:
        START_FROM = args.s
    else:
        START_FROM = 0
    if args.e:
        END_AT = args.e

    a = datetime.datetime.now().replace(microsecond=0)
    rgraph = uritools.get_organization(config['ORG_URI'], 
                                       config['ORG_NAME'], 
                                       config['ORG_SAME_AS'],
                                       config['ORG_CONTACT_NAME'],
                                       config['ORG_CONTACT_EMAIL'],
                                       config['ORG_ISIL'],
                                       config['ORG_ALTNAME'])

    try:
        adlib_harvester.harvest(rgraph, 
                                endpoint=config['SRC_URI'], 
                                database=config['SRC_DB'], 
                                make_stats=False,
                                start_from=START_FROM,
                                end_at=END_AT, 
                                apilimit=config['SRC_API_LIMIT'])
    except Exception as e:
        logger.error('Harvesting failed: %s', str(e))
    finally:
        b = datetime.datetime.now().replace(microsecond=0)
        dt = b-a
        records = len(list(rgraph.subjects(RDF.type, SDO.ArchiveComponent)))
        dt_avg = (dt/records) / datetime.timedelta(milliseconds=1) 
        logger.info('Finished after %s, average time spent per record %s ms.', str(dt), str(dt_avg))
        logger.info('Writing  %s', f'{OUTPUT_FILE_FORMAT} file to {ARTIFACT_PATH}')
        rgraph.serialize(format=OUTPUT_FILE_FORMAT, 
                         destination=ARTIFACT_PATH, 
                         encoding=ENCODING, 
                         auto_compact=True,
                         )  
        logger.info("Filesize:  %s", f"{(os.path.getsize(ARTIFACT_PATH) / 1000)} KB")

if __name__ == '__main__':
    main()