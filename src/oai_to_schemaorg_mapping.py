from rdflib.namespace import SDO, XSD
from rdflib import RDF, Literal, URIRef
import oai_xpaths

# Records zijn van de volgende types.
RECORD_OBJECT_TYPES = [
    SDO.CreativeWork,
    SDO.ArchiveComponent,
    SDO.ItemList,
]

### Velden in DEFINED_TERM_TYPES kunnen verrijkingen bevatten. ###
# in DEFINED_TERM_TYPES is aangegeven wat de rdf:Type van de defined term is per xpath
DEFINED_TERM_TYPES = {
    oai_xpaths.MATERIAL_ITEM: [SDO.Product, SDO.DefinedTerm],
    oai_xpaths.OBJECT_CATEGORY: [SDO.DefinedTerm],
    oai_xpaths.ASSOCIATION_SUBJECT: [SDO.DefinedTerm],
    oai_xpaths.PRODUCTION_PLACE: [SDO.Place, SDO.DefinedTerm]
}
# in DEFINED_TERM_FIELD_MAPPING is opgenomen wat de verhouding is met het CreativeWork object, dus welk predicaat gebruikt wordt
# daarna komt de term en daarna de uri
DEFINED_TERM_FIELD_MAPPING = {
    oai_xpaths.MATERIAL_ITEM: [SDO.material, oai_xpaths.TERM_NAME, oai_xpaths.TERM_URI],
    oai_xpaths.OBJECT_CATEGORY: [SDO.genre, oai_xpaths.TERM_NAME, oai_xpaths.TERM_URI],
    oai_xpaths.ASSOCIATION_SUBJECT: [SDO.about, oai_xpaths.TERM_NAME, oai_xpaths.TERM_URI],
    oai_xpaths.PRODUCTION_PLACE: [SDO.locationCreated, oai_xpaths.TERM_NAME, oai_xpaths.TERM_URI],
} 

# mapping voor velden die als property-value toegevoegd worden 
# PropertyValue mapping: map field a: [b, c] to SDO.value [a], predicate [b], SDO.propertyID [c], SDO.description [d], 
PROPERTY_VALUE_MAPPING = {
    oai_xpaths.OBJECT_NUMBER: [SDO.identifier, Literal('https://documentation.axiell.com/alm/en/index.html?ds_eiefxml.html', datatype=XSD.anyURI), 'AdlibXML object_number'],
}

# directe attributen van het CreativeWork
BASIC_MAPPING = {
    oai_xpaths.DESCRIPTION_TEXT: [SDO.description, Literal, XSD.string],
    oai_xpaths.OBJECT_NAME_ITEM: [SDO.name, Literal, XSD.string],
    oai_xpaths.DIMENSION_FREE: [SDO.size, Literal, XSD.string],
    oai_xpaths.PRODUCTION_DATE_END: [SDO.dateCreated, Literal, XSD.string],
    oai_xpaths.TITLE_TEXT: [SDO.name, Literal, XSD.string],
}

# mapping voor attributen mbt rechten
RIGHTS_MAPPING = {
    oai_xpaths.RIGHTS_HOLDER: SDO.copyrightHolder,
}

# mapping voor attributen mbt maker, creator is altijd een persoon
CREATOR_MAPPING = {
    oai_xpaths.CREATOR_NAME: [SDO.name, Literal, XSD.string], 
    oai_xpaths.RKDARTISTS: [SDO.sameAs, URIRef, None], 
    oai_xpaths.CREATOR_DATE_OF_DEATH: [SDO.deathDate, Literal, XSD.string],
    oai_xpaths.CREATOR_DATE_OF_BIRTH: [SDO.birthDate, Literal, XSD.string],
}

CREATOR_DEFINED_TERM_TYPES = {
    oai_xpaths.CREATOR_ROLE: [SDO.Occupation, SDO.DefinedTerm],
}

CREATOR_DEFINED_TERM_MAPPING = {
    oai_xpaths.CREATOR_ROLE: [SDO.hasOccupation, oai_xpaths.TERM_NAME, oai_xpaths.TERM_URI],
}

# mapping voor simpele afmetingen
DIMENSION_MAPPING = {
    oai_xpaths.DIMENSION_UNIT: SDO.unitText,
    oai_xpaths.DIMENSION_VALUE: SDO.value,
}

# mapping voor andere tijdsaanduidingen
TEMPORAL_INFO_MAPPING = {
    #oai_xpaths.PRODUCTION_DATE_START: [],
    oai_xpaths.PRODUCTION_DATE_END: [SDO.dateCreated, SDO.temporal],
    oai_xpaths.CREATOR_DATE_OF_BIRTH: [SDO.birthDate, SDO.birthDate],
    oai_xpaths.CREATOR_DATE_OF_DEATH: [SDO.deathDate, SDO.deathDate],
}

# MediaObject, ImageObject
# thumbnail (required)


# mapping voor link naar afbeelding
REPRODUCTION_MAPPING = {
    oai_xpaths.REPRODUCTION_REFERENCE: [SDO.associatedMedia, SDO.MediaObject, SDO.contentUrl, SDO.encodesCreativeWork, URIRef('https://rightsstatements.org/page/InC/1.0/?language=nl')]
}

MEDIAOBJECT_MAPPING = {
    RDF.type: SDO.MediaObject,
    SDO.contentUrl: oai_xpaths.REPRODUCTION_REFERENCE,
    SDO.license: Literal('https://rightsstatements.org/page/InC/1.0/?language=nl', datatype=XSD.anyURI),
}
