from rdflib import Graph
from shexer.shaper import Shaper
from shexer.consts import NT, SHEXC, SHACL_TURTLE, JSON_LD

target_classes = [
    "https://schema.org/CreativeWork",
    "https://schema.org/Person",
    "https://schema.org/DefinedTerm",
    "https://schema.org/QuantitativeValue",
    "https://schema.org/MediaObject",
    "https://schema.org/PropertyValue",
]

namespaces_dict = {"http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
                   "https://schema.org/": "sdo",
                   "http://www.w3.org/2001/XMLSchema#": "xsd"
                   }

def main():

    shaper = Shaper(target_classes=target_classes,
                    graph_file_input='aggregate-kc.jsonld',
                    input_format=JSON_LD,
                    #namespaces_dict=namespaces_dict,  # Default: no prefixes
                    instantiation_property="http://www.w3.org/1999/02/22-rdf-syntax-ns#type")  # Default rdf:type

    output_file = "datashape.shex"

    shaper.shex_graph(output_file=output_file,
                    acceptance_threshold=0.1)

if __name__ == '__main__':
    main()