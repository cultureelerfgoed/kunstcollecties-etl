import os
import logging
from rdflib import Graph
import adlib_transformer

logger = logging.getLogger(__name__)
path = 'data/output/rubenpriref24099.adlib.xml'

def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    rgraph = Graph()

    dir_path = 'data/output/'
    limit = 100

    for index, filename in enumerate(os.listdir(dir_path)):
        if not filename.endswith('.xml'): continue
        path = os.path.join(dir_path, filename)
        rgraph = rgraph +  adlib_transformer.parse_path_to_graph(path)
        
        if index >= limit:
            break

    rgraph.print()

if __name__ == '__main__':
    main()