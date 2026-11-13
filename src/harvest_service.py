import os
import sys
import json
import logging
import datetime
import argparse
import yaml
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import SDO, RDF, DC
import uritools
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
    # aantal records dat mag falen bij de transformatie voordat de run als mislukt geldt
    max_record_errors = int(config.get('MAX_RECORD_ERRORS', 0))
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    parser = argparse.ArgumentParser("Rijkscollectie-RCE ETL")
    parser.add_argument("--chunks", help="Number of records per json-ld file.", type=int)
    parser.add_argument("--testmode", help="Only run first chunk for testing.", type=str)

    args = parser.parse_args()
    if args.chunks:
        CHUNK_SIZE = args.chunks
    if args.testmode:
        TESTMODE = (str(args.testmode).lower() == 'true')

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
        dataset_node = URIRef('https://linkeddata.cultureelerfgoed.nl/rce/rijkscollectie-rce/')
        rgraph = Graph()
        rgraph.add((dataset_node, RDF.type, SDO.Dataset))
        rgraph.add((dataset_node, SDO.url, URIRef('https://kennis.cultureelerfgoed.nl/index.php/Dataset/103')))
        rgraph.add((dataset_node, DC.title, Literal('Rijkscollectie RCE', lang='nl')))
        org_graph = uritools.get_organization(config['ORG_URI'], 
                                                config['ORG_NAME'], 
                                                config['ORG_SAME_AS'],
                                                config['ORG_CONTACT_NAME'],
                                                config['ORG_CONTACT_EMAIL'],
                                                config['ORG_ISIL'],
                                                config['ORG_ALTNAME'])
        rgraph = rgraph + org_graph
        rgraph.add((dataset_node, SDO.publisher, URIRef(config['ORG_URI'])))
        a = datetime.datetime.now().replace(microsecond=0)

        # Fouten bij het ophalen laten we bewust doorlopen: een run die stilzwijgend een deel mist,
        # is erger dan een run die faalt (de publicatiestap wordt dan niet uitgevoerd).
        rgraph = harvester.harvest(rgraph,
                    base_url=config['SRC_URI'],
                    verb='ListRecords',
                    metadata_prefix='kc_rs',
                    set_spec=config['SRC_DB'],
                    max_items=CHUNK_SIZE,
                    state=persistant_state)
        records = len(list(rgraph.subjects(RDF.type, SDO.CreativeWork)))
        finished = persistant_state.get('resumptionToken', '').strip() == ''

        # Ook de LAATSTE chunk (de rest na de laatste volle chunk) moet worden weggeschreven.
        # Voorheen stopte de loop hier met 'break' voordat er geserialiseerd werd, waardoor
        # de laatste records (bij 134.165 records en chunks van 7000: 1.165) nooit gepubliceerd werden.
        if records > 0:
            b = datetime.datetime.now().replace(microsecond=0)
            dt = b-a
            dt_avg = (dt/records) / datetime.timedelta(milliseconds=1)
            logger.info('Finished chunk after %s, got %i records, avg time spent per record %s ms, total records seen: %i.', str(dt), records, str(dt_avg), persistant_state.get('seen', 0))
            logger.info('rt: %s', persistant_state.get('resumptionToken'))
            path = f'{CACHE_PATH}kc-pt-{index}.jsonld'
            logger.info('Writing  %s', f'{OUTPUT_FILE_FORMAT} file to {path}')
            rgraph.serialize(format=OUTPUT_FILE_FORMAT,
                            destination=path,
                            encoding=ENCODING,
                            auto_compact=True)
            logger.info("Filesize:  %s", f"{(os.path.getsize(path) / 1000)} KB")
            persistant_state['written'] = persistant_state.get('written', 0) + records
            persistant_state['files'] = persistant_state.get('files', 0) + 1

        if finished or records == 0:
            logger.info('Reached end of records from source API, records seen: %i, exiting..', persistant_state.get("seen", 0))
            break
    else:
        # for-else: de range is op zonder dat de bron leeg was (MAX_RECORDS te laag)
        if not TESTMODE:
            logger.error('MAX_RECORDS (%i) bereikt voordat de bron leeg was; de oogst is onvolledig.', MAX_RECORDS)
            write_manifest(CACHE_PATH, persistant_state, complete=False)
            sys.exit(1)

    complete = verify_completeness(persistant_state, TESTMODE, max_record_errors)
    write_manifest(CACHE_PATH, persistant_state, complete=complete)
    if not complete:
        sys.exit(1)


def verify_completeness(state: dict, testmode: bool, max_record_errors: int = 0) -> bool:
    """Vergelijk wat we gezien en verwerkt hebben met wat de bron aankondigt (completeListSize)."""
    logger = logging.getLogger(__name__)
    if testmode:
        logger.info('Testmode: volledigheidscontrole overgeslagen.')
        return True
    expected = state.get('complete_list_size')
    seen = state.get('seen', 0)
    errors = state.get('errors', 0)
    ok = True
    if expected is None:
        logger.warning('De bron gaf geen completeListSize; volledigheid kan niet worden gecontroleerd.')
    elif seen != expected:
        logger.error('ONVOLLEDIG: bron kondigt %i records aan, %i opgehaald.', expected, seen)
        ok = False
    if state.get('written', 0) < seen - state.get('skipped', 0) - errors:
        logger.error('Niet alle opgehaalde records staan in de uitvoerbestanden (%i van %i).', state.get('written', 0), seen)
        ok = False
    if errors > max_record_errors:
        logger.error('%i records konden niet (volledig) getransformeerd worden (toegestaan: %i): %s',
                     errors, max_record_errors, ', '.join(state.get('error_ids', [])[:20]))
        ok = False
    logger.info('Controle: bron=%s, opgehaald=%i, overgeslagen=%i, fouten=%i, weggeschreven=%i -> %s',
                expected, seen, state.get('skipped', 0), errors, state.get('written', 0), 'OK' if ok else 'MISLUKT')
    return ok


def write_manifest(cache_path: str, state: dict, complete: bool):
    """Schrijf een klein verslag naast de uitvoerbestanden, zodat een run achteraf controleerbaar is."""
    manifest = {k: state.get(k) for k in ('complete_list_size', 'seen', 'skipped', 'errors', 'written', 'files')}
    manifest['error_ids'] = state.get('error_ids', [])[:200]
    manifest['complete'] = complete
    manifest['finished_at'] = datetime.datetime.now().replace(microsecond=0).isoformat()
    with open(f'{cache_path}manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

if __name__ == '__main__':
    main()