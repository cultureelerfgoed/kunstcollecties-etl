#! /usr/bin/env python3
import urllib.request
import os
import logging
from rdflib import Graph
import xml.etree.ElementTree as ET
import adlib_transformer
import adlib_xpaths as xpath

logger = logging.getLogger(__name__)
apiLimit = 1000

GRAPH_ID = os.getenv('GRAPH_ID', 'default')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
ARTIFACT_PATH = os.getenv('ARTIFACT_PATH', 'kc.jsonld')
ENCODING = os.getenv('ENCODING', 'utf-8')
LIMIT = int(os.getenv('LIMIT', 141058)) # should be divisible by apiLimit

def harvest(endpoint: str, database='collect', search='all', xmltype='grouped', test=False) -> Graph:
    ## initialize variables for loop
    page = 0
    rgraph = adlib_transformer.get_organization()
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

        result = urllib.request.urlopen(requestUrl)
        adlibXML = result.read()
        root = ET.fromstring(adlibXML)

        # get detailed information with priref
        r_list = root.findall('.//record')
        if len(r_list) > 0:
            for record in r_list:
                # parse adlibXML
                try:
                    rgraph = rgraph +  adlib_transformer.parse_tree_to_graph(record)
                    r_iter = r_iter + 1
                    stats = adlib_transformer.combine_stats(stats, adlib_transformer.make_statistics_from_string(adlibXML))
                except TypeError as te:
                    logger.warning('Failed to find an element: %s', te)
        else:
            break

        page = page + 1
        logger.info('Harvested %s out of %s records', str(page * apiLimit) + '-' + str(page * apiLimit + apiLimit), str(LIMIT))

    adlib_transformer.print_stats(stats)
    return rgraph
