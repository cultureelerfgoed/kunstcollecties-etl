from rdflib.namespace import SDO, XSD
from rdflib import Literal
import adlib_xpaths

# Records zijn van de volgende types.
RECORD_OBJECT_TYPES = [
    SDO.CreativeWork,
    SDO.ArchiveComponent,
    SDO.ItemList,
]

### Velden in DEFINED_TERM_TYPES kunnen verrijkingen bevatten. ###
# in DEFINED_TERM_TYPES is aangegeven wat de rdf:Type van de defined term is per xpath
DEFINED_TERM_TYPES = {
    adlib_xpaths.MATERIAL: [SDO.Product, SDO.DefinedTerm],
    adlib_xpaths.OBJECT_CATEGORY: [SDO.DefinedTerm],
    adlib_xpaths.ASSOCIATION_SUBJECT: [SDO.DefinedTerm],
    adlib_xpaths.PRODUCTION_PLACE_SRC_TERM: [SDO.Place, SDO.DefinedTerm]
}
# in DEFINED_TERM_FIELD_MAPPING is opgenomen wat de verhouding is met het CreativeWork object, dus welk predicaat gebruikt wordt
# daarna komt de term en daarna de uri
DEFINED_TERM_FIELD_MAPPING = {
    adlib_xpaths.MATERIAL: [SDO.material, adlib_xpaths.MATERIAL_NAME, adlib_xpaths.MATERIAL_SRC_URI],
    adlib_xpaths.OBJECT_CATEGORY: [SDO.genre, adlib_xpaths.OBJECT_CATEGORY, adlib_xpaths.OBJECT_CATEGORY_SRC_URI],
    adlib_xpaths.ASSOCIATION_SUBJECT: [SDO.additionalType, adlib_xpaths.ASSOCIATION_SUBJECT, adlib_xpaths.ASSOCIATION_SUBJECT_SRC_URI],
    adlib_xpaths.PRODUCTION_PLACE_SRC_TERM: [SDO.locationCreated, adlib_xpaths.PRODUCTION_PLACE_SRC_TERM, adlib_xpaths.PRODUCTION_PLACE_SRC_URI],
} 

# mapping voor velden die als property-value toegevoegd worden 
# PropertyValue mapping: map field a: [b, c] to SDO.value [a], predicate [b], SDO.propertyID [c], SDO.description [d], 
PROPERTY_VALUE_MAPPING = {
    adlib_xpaths.OBJECT_NUMBER: [SDO.identifier, Literal('https://documentation.axiell.com/alm/en/index.html?ds_eiefxml.html', datatype=XSD.anyURI), 'AdlibXML object_number'],
    adlib_xpaths.PRIREF: [SDO.identifier, Literal('https://documentation.axiell.com/alm/en/index.html?ds_eiefxml.html', datatype=XSD.anyURI), 'AdlibXML priref'],
}

# directe attributen van het CreativeWork
BASIC_MAPPING = {
    adlib_xpaths.DESCRIPTION_TEXT: [SDO.description, Literal, XSD.string],
    adlib_xpaths.OBJECT_NAME_ITEM: [SDO.name, Literal, XSD.string],
    adlib_xpaths.DIMENSION_FREE: [SDO.size, Literal, XSD.string],
    adlib_xpaths.PRODUCTION_DATE_END: [SDO.dateCreated, Literal, XSD.string],
    adlib_xpaths.TITLE_TEXT: [SDO.name, Literal, XSD.string],
}

# mapping voor attributen mbt rechten
RIGHTS_MAPPING = {
    adlib_xpaths.RIGHTS_HOLDER: SDO.copyrightHolder,
}

# mapping voor attributen mbt maker, creator is altijd een persoon
CREATOR_MAPPING = {
    adlib_xpaths.CREATOR_NAME: [SDO.name, Literal, XSD.string], 
    adlib_xpaths.RKDARTISTS: [SDO.sameAs, Literal, XSD.anyURI], 
    adlib_xpaths.CREATOR_DATE_OF_DEATH: [SDO.deathDate, Literal, XSD.string],
    adlib_xpaths.CREATOR_DATE_OF_BIRTH: [SDO.birthDate, Literal, XSD.string],
    adlib_xpaths.CREATOR_ROLE: [SDO.hasOccupation, Literal, XSD.string],
}

CREATOR_DEFINED_TERM_TYPES = {
}

CREATOR_DEFINED_TERM_MAPPING = {
}

# mapping voor simpele afmetingen
DIMENSION_MAPPING = {
    adlib_xpaths.DIMENSION_UNIT: SDO.unitText,
    adlib_xpaths.DIMENSION_VALUE: SDO.value,
}

# mapping voor link naar afbeelding
REPRODUCTION_MAPPING = {
    adlib_xpaths.REPRODUCTION_REFERENCE: [SDO.associatedMedia, SDO.MediaObject, SDO.contentUrl, SDO.encodesCreativeWork]
}
