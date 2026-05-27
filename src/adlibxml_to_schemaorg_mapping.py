from rdflib.namespace import SDO, XSD
from rdflib import Literal
import adlib_xpaths

# Records zijn van de volgende types.
RECORD_OBJECT_TYPES = [
    SDO.CreativeWork,
    SDO.ArchiveComponent,
    SDO.ItemList,
]

### Voor velden in DEFINED_TERM_TYPES wordt een poging gedaan om via de CHT Rest API te verrijken als ENRICH_TERMS in de config op 'True' staat. ###
# in DEFINED_TERM_TYPES is aangegeven wat de rdf:Type van de defined term is per xpath
DEFINED_TERM_TYPES = {
    adlib_xpaths.MATERIAL_ITEM: [SDO.DefinedTerm, SDO.URL],
    adlib_xpaths.OBJECT_CATEGORY: [SDO.DefinedTerm],
    adlib_xpaths.ASSOCIATION_SUBJECT: [SDO.DefinedTerm, SDO.URL],
}
# in DEFINED_TERM_FIELD_MAPPING is opgenomen wat de verhouding is met het CreativeWork object, dus welk predicaat gebruikt wordt
DEFINED_TERM_FIELD_MAPPING = {
    adlib_xpaths.MATERIAL_ITEM: SDO.material,
    adlib_xpaths.OBJECT_CATEGORY: SDO.genre,
    adlib_xpaths.ASSOCIATION_SUBJECT: SDO.additionalType,
} 

# mapping voor locatie-gerelateerde velden
LOCATION_FIELDS = {
    adlib_xpaths.PRODUCTION_PLACE: [SDO.locationCreated, SDO.Place],
}

# mapping voor velden die als property-value toegevoegd worden 
# PropertyValue mapping: map field a: [b, c] to SDO.value [a], SDO.propertyID [b], SDO.description [c], 
PROPERTY_VALUE_MAPPING = {
    adlib_xpaths.OBJECT_NUMBER: [SDO.identifier, 'AdlibXML object_number']
}

# directe attributen van het CreativeWork
BASIC_MAPPING = {
    adlib_xpaths.DESCRIPTION_TEXT: [SDO.description, Literal, XSD.string],
    adlib_xpaths.OBJECT_NAME_ITEM: [SDO.description, Literal, XSD.string],
    adlib_xpaths.DIMENSION_FREE: [SDO.description, Literal, XSD.string],
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

# mapping voor simpele afmetingen
DIMENSION_MAPPING = {
    adlib_xpaths.DIMENSION_UNIT: SDO.unitText,
    adlib_xpaths.DIMENSION_VALUE: SDO.value,
}

# mapping voor link naar afbeelding
REPRODUCTION_MAPPING = {
    adlib_xpaths.REPRODUCTION_REFERENCE: [SDO.associatedMedia, SDO.MediaObject, SDO.contentUrl, SDO.encodesCreativeWork]
}
