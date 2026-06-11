import logging
import traceback
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from rdflib import Graph

logger = logging.getLogger(__name__)

def harvest(target_graph: Graph, endpoint: str, db='collect', prefix='rs', xmltype='grouped', make_stats=False, start_from=0, end_at=200000, apilimit = 500) -> Graph:
    client = Client(endpoint)
    client.listRecords()

    for record in client.listRecords(metadataPrefix=prefix, database=db):
        print(record)
