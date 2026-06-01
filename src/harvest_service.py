import os
import traceback
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
    OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')

    # default chunks
    CHUNK_SIZE = 8000
    # hard limit for records
    MAX_RECORDS = 200000

    config = yaml.safe_load(open(CONFIG_PATH, encoding=ENCODING))
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    parser = argparse.ArgumentParser("Kunstcollecties ETL")
    parser.add_argument("--chunks", help="Number of records per json-ld file.", type=int)

    args = parser.parse_args()
    if args.chunks:
        CHUNK_SIZE = args.chunks
    
    for index in range(0, int(MAX_RECORDS/CHUNK_SIZE)):
        records = 0
        rgraph = uritools.get_organization(config['ORG_URI'], 
                                            config['ORG_NAME'], 
                                            config['ORG_SAME_AS'],
                                            config['ORG_CONTACT_NAME'],
                                            config['ORG_CONTACT_EMAIL'],
                                            config['ORG_ISIL'],
                                            config['ORG_ALTNAME'])
        a = datetime.datetime.now().replace(microsecond=0)
        try:
            adlib_harvester.harvest(rgraph, 
                                    endpoint=config['SRC_URI'], 
                                    database=config['SRC_DB'], 
                                    make_stats=False,
                                    start_from=index*CHUNK_SIZE,
                                    end_at=(index+1)*CHUNK_SIZE, 
                                    apilimit=config['SRC_API_LIMIT'])
            records = len(list(rgraph.subjects(RDF.type, SDO.ArchiveComponent)))
        except AssertionError as e:
            logger.error('Harvesting failed: %s', str(traceback.format_exception(e)))
        
        if records == 0:
            logger.info('Reached end of records from source API, exiting..')
            break
        else:
            b = datetime.datetime.now().replace(microsecond=0)
            dt = b-a
            dt_avg = (dt/records) / datetime.timedelta(milliseconds=1)
            logger.info('Finished after %s, average time spent per record %s ms.', str(dt), str(dt_avg))
            path = f'kc-pt-{index}.jsonld'
            logger.info('Writing  %s', f'{OUTPUT_FILE_FORMAT} file to {path}')
            rgraph.serialize(format=OUTPUT_FILE_FORMAT, 
                            destination=path, 
                            encoding=ENCODING, 
                            auto_compact=True)  
            logger.info("Filesize:  %s", f"{(os.path.getsize(path) / 1000)} KB")

if __name__ == '__main__':
    main()