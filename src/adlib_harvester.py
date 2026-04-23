#! /usr/bin/env python3
import datetime
import urllib.request
import os
import logging
from rdflib import Graph
import xml.etree.ElementTree as ET
import adlib_transformer

logger = logging.getLogger(__name__)
apiLimit = 100

OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
ARTIFACT_PATH = os.getenv('ARTIFACT_PATH', 'kc.jsonld')
ENCODING = os.getenv('ENCODING', 'utf-8')
LIMIT = int(os.getenv('LIMIT', 100)) # max 141058 records
MODIFIED_ON_OR_AFTER = datetime.datetime.strptime(os.getenv('MODIFIED_ON_OR_AFTER', '1970-01-01'), '%Y-%m-%d')

def harvest(target_graph: Graph, endpoint: str, database='collect', search='all', xmltype='grouped', make_stats=False) -> Graph:
    ## initialize variables for loop
    page = 0
    stats = {}
    r_iter = 0

    # iterate through resultpages
    while (LIMIT > 0 and r_iter < LIMIT):
        startfrom = page * apiLimit
        # read page of records
        requestUrl = endpoint + \
                        "?database=" + database + \
                        "&search=" + search + \
                        "&XMLtype=" + xmltype + \
                        "&limit=" + str(apiLimit) + \
                        "&startfrom=" + str(startfrom)

        result = urllib.request.urlopen(requestUrl, timeout=90)
        adlibXML = result.read()
        root = ET.fromstring(adlibXML)

        # get detailed information with priref
        r_list = root.findall('.//record')
        if len(r_list) > 0:
            for record in r_list:
                mod_txt = record.attrib['modification']
                mod_dt = datetime.datetime.strptime(mod_txt, '%Y-%m-%dT%H:%M:%S')
                # parse adlibXML
                r_iter = r_iter + 1
                if mod_dt >= MODIFIED_ON_OR_AFTER:
                    try:
                        adlib_transformer.parse_tree_to_graph(target_graph, record)
                        if make_stats:
                            stats = adlib_transformer.combine_stats(stats, adlib_transformer.make_statistics_from_string(ET.tostring(record)))
                    except TypeError as te:
                        logger.warning('TypeError: %s', te)
        else:
            break

        logger.info('Harvested %s out of %s records', str(page * apiLimit) + '-' + str(page * apiLimit + apiLimit), str(LIMIT))
        page = page + 1

    if make_stats:
        adlib_transformer.print_stats(stats)
    return target_graph
