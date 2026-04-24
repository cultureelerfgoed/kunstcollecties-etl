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
LIMIT = int(os.getenv('LIMIT', 0)) # max 141058 records
MODIFIED_ON_OR_AFTER = datetime.datetime.strptime(os.getenv('MODIFIED_ON_OR_AFTER', '1970-01-01'), '%Y-%m-%d')

def harvest(target_graph: Graph, endpoint: str, database='collect', search='all', xmltype='grouped', make_stats=False, start_from_record=None) -> Graph:
    ## initialize variables for loop
    stats = {}
    max_r = 200000
    if start_from_record:
        page = int(start_from_record / apiLimit)
        r_iter = start_from_record
    else:
        page = 0
        r_iter = 0

    # iterate through resultpages
    while (LIMIT == 0 or r_iter < LIMIT < max_r):
        startfrom = page * apiLimit
        # read page of records
        requestUrl = endpoint + \
                        "?database=" + database + \
                        "&search=" + search + \
                        "&XMLtype=" + xmltype + \
                        "&limit=" + str(apiLimit) + \
                        "&startfrom=" + str(startfrom)
        
        try:
            result = urllib.request.urlopen(requestUrl, timeout=90)
            adlibXML = result.read()
            root = ET.fromstring(adlibXML)
            # get detailed information with priref
            r_list = root.findall('.//record')
        except (TimeoutError, OSError) as re:
            logger.warning('Error while getting the page: %s', str(re))

        if len(r_list) > 0:
            max_r = int(root.find('.//hits').text) # get amount of hits from page containing records
            for record in r_list:
                # parse adlibXML
                r_iter = r_iter + 1
                try:
                    adlib_transformer.parse_tree_to_graph(target_graph, record)
                    if make_stats:
                        stats = adlib_transformer.combine_stats(stats, adlib_transformer.make_statistics_from_string(ET.tostring(record)))
                except (TypeError, AssertionError) as te:
                    logger.warning('Error during transformation: %s', te)
        else:
            logger.info('Reached end of records.')
            break

        logger.info('Harvested %s out of %s records, found %i records', str(page * apiLimit) + '-' + str(page * apiLimit + apiLimit), str(max_r), len(r_list))
        page = page + 1

    if make_stats:
        adlib_transformer.print_stats(stats)
    return target_graph
