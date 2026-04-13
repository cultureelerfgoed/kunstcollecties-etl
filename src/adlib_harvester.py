#! /usr/bin/env python3
import lxml.etree as etree
import urllib.request
import os
import logging
import datetime
import adlib_transformer
from rdflib import Graph

logger = logging.getLogger(__name__)
limit = 100

GRAPH_ID = os.getenv('GRAPH_ID', 'default')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'kc.jsonld')
ENCODING = os.getenv('ENCODING', 'utf-8')

def harvest(endpoint: str, database='collect', search='all', xmltype='grouped', test=False) -> Graph:
    ## initialize variables for loop
    page = 0
    numberFound = 1000000
    rgraph = Graph()
    stats = {}
    date = datetime.datetime.strptime('1900-01-01', '%Y-%m-%d')

    # iterate through resultpages
    while (numberFound > (page * limit)):
        startfrom = page * limit
        # read page of records
        requestUrl = endpoint + \
                        "?database=" + database + \
                        "&search=" + search + \
                        "&XMLtype=" + xmltype + \
                        "&limit=" + str(limit) + \
                        "&startfrom=" + str(startfrom)

        result = urllib.request.urlopen(requestUrl)
        adlibXML = result.read()

        # parse adlibXML
        dom = etree.fromstring(adlibXML)

        # get detailed information with priref
        for record in dom.findall('.//record'):
            priref = record.get('priref')
            modification = record.get('modification')
            mod = datetime.datetime.strptime(modification, '%Y-%m-%dT%H:%M:%S')
            if mod > date:
                requestUrl = endpoint + \
                "?database=" + database + \
                "&search=priref=" + priref + \
                "&XMLtype=" + xmltype

                result = urllib.request.urlopen(requestUrl)
                adlibXML = result.read()

                # parse adlibXML
                dom2 = etree.fromstring(adlibXML)
                adlibXML = etree.tostring(dom2, pretty_print=True)

                try:
                    rgraph = rgraph +  adlib_transformer.parse_string_to_graph(adlibXML)
                    stats = adlib_transformer.combine_stats(stats, adlib_transformer.make_statistics_from_string(adlibXML))
                except TypeError as te:
                    logger.warning('Failed to find an element: %s', te)

        # make loop end
        ## read numberFound
        hits = dom.find(".//hits")
        numberFound = int(hits.text)
        if test:
            numberFound = 1000 # maximum for testing

        page = page + 1
        logger.info(str(page * limit) + "-" + str(page * limit + limit) + " of " + str(numberFound))

    adlib_transformer.print_stats(stats)
    return rgraph
