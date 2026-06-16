#! /usr/bin/env python3
import urllib.request
import logging
import traceback
import xml.etree.ElementTree as ET
from rdflib import Graph
from requests import HTTPError
import transform_service
import adlibxml_to_schemaorg_mapping as mapping

logger = logging.getLogger(__name__)

def harvest(target_graph: Graph, endpoint: str, database='collect', search='all', xmltype='grouped', make_stats=True, start_from=0, end_at=200000, apilimit = 500) -> Graph:
    ## initialize variables for loop
    stats = {}
    if start_from:
        page = int(start_from / apilimit)
        r_iter = start_from
    else:
        page = 0
        r_iter = 0

    # iterate through resultpages
    while (r_iter < end_at):
        startfrom = page * apilimit
        # read page of records
        requestUrl = endpoint + \
                        "?database=" + database + \
                        "&search=" + search + \
                        "&XMLtype=" + xmltype + \
                        "&limit=" + str(apilimit) + \
                        "&startfrom=" + str(startfrom)
        
        try:
            result = urllib.request.urlopen(requestUrl, timeout=180)    
        except (TimeoutError, OSError, HTTPError) as re:
            logger.warning('Error while getting the page: %s', str(traceback.format_exception(re)))
            logger.warning('Retrying the page..')
            result = urllib.request.urlopen(requestUrl, timeout=240)

        adlibXML = result.read()
        root = ET.fromstring(adlibXML)
        # get detailed information with priref
        r_list = root.findall('.//record')

        if len(r_list) > 0:
            hits = root.find('.//hits')
            if hits is not None and hits.text is not None:
                max_r = int(hits.text) # get amount of hits from page containing records
            else:
                max_r = 0
                
            for record in r_list:
                # parse adlibXML
                r_iter = r_iter + 1
                try:
                    transform_service.parse_tree_to_graph(target_graph, record, mapping)
                    if make_stats:
                        stats = transform_service.combine_stats(stats, transform_service.make_statistics_from_string(str(ET.tostring(record))))
                except (AssertionError, TypeError) as te:
                    logger.warning('Error during transformation: %s', str(traceback.format_exception(te)))
        else:
            break

        logger.debug('Harvested %s out of %s records, found %i records on page, harvested %i total', str(page * apilimit) + '-' + str(page * apilimit + apilimit), str(max_r), len(r_list), r_iter - start_from)
        page = page + 1

    if make_stats:
        transform_service.print_stats(stats)
    return target_graph
