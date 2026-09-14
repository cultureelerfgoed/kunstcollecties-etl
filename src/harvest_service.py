import os
import traceback
import logging
import datetime
import argparse
import yaml
from rdflib import Graph
from rdflib.namespace import SDO, RDF
import oai_harvester as harvester

def main():
    """ main runner for workflow """

    CONFIG_PATH = os.getenv('CONFIG_PATH', 'config/config.yml')
    ENCODING = os.getenv('ENCODING', 'utf-8')
    OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
    CACHE_PATH = os.getenv('CACHE_PATH', 'data/')

    # default chunks
    CHUNK_SIZE = 8000
    # hard limit for records
    MAX_RECORDS = 200000
    # default testmode off
    TESTMODE = False

    config = yaml.safe_load(open(CONFIG_PATH, encoding=ENCODING))
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    parser = argparse.ArgumentParser("Rijkscollectie-RCE ETL")
    parser.add_argument("--chunks", help="Number of records per json-ld file.", type=int)
    parser.add_argument("--testmode", help="Only run first chunk for testing.", type=bool)

    args = parser.parse_args()
    if args.chunks:
        CHUNK_SIZE = args.chunks
    if args.testmode:
        TESTMODE = args.testmode

    logger.info('Starting harvest of \n endpoint: %s \n enriching terms: %s \n pushing to: %s \n testmode: %s \n', config['SRC_URI'], config['ENRICH_TERMS'], config['BASE_URI']+config['COLLECTION_ID'], str(TESTMODE))
    persistant_state = {
                "total": 0,
                "resumptionToken": "",
    }

    if TESTMODE:
        h_range = range(0,1)
    else:
        h_range = range(0, int(MAX_RECORDS/CHUNK_SIZE))

    for index in h_range:
        records = 0
        rgraph = Graph()
        a = datetime.datetime.now().replace(microsecond=0)

        try:
            rgraph = harvester.harvest(rgraph,
                        base_url=config['SRC_URI'],
                        verb='ListRecords',
                        metadata_prefix='kc_rs',
                        set_spec=config['SRC_DB'],
                        max_items=CHUNK_SIZE,
                        state=persistant_state)
            records = len(list(rgraph.subjects(RDF.type, SDO.CreativeWork)))

        except TypeError as e: # Exception as e:
            logger.error('Harvesting failed: %s', str(traceback.format_exception(e)))
        
        if records == 0 or persistant_state.get('resumptionToken', '').strip() == '':
            logger.info('Reached end of records from source API, total retrieved records: %i, exiting..', persistant_state.get("total"))
            break
        else:
            b = datetime.datetime.now().replace(microsecond=0)
            dt = b-a
            total = int(persistant_state.get('total', 0))
            dt_avg = (dt/records) / datetime.timedelta(milliseconds=1)
            logger.info('Finished chunk after %s, got %i records, avg time spent per record %s ms, total records harvested: %i.', str(dt), records, str(dt_avg), total)
            logger.info('rt: %s', persistant_state.get('resumptionToken'))
            path = f'{CACHE_PATH}kc-pt-{index}.jsonld'
            logger.info('Writing  %s', f'{OUTPUT_FILE_FORMAT} file to {path}')
            rgraph.serialize(format=OUTPUT_FILE_FORMAT,
                            destination=path,
                            encoding=ENCODING,
                            auto_compact=True)
            logger.info("Filesize:  %s", f"{(os.path.getsize(path) / 1000)} KB")

if __name__ == '__main__':
    main()