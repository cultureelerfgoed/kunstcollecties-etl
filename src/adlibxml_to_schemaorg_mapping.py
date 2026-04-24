from rdflib.namespace import SDO
from rdflib import URIRef, Literal
import adlib_xpaths

RECORD_OBJECT_TYPES = [
    SDO.CreativeWork,
    SDO.ArchiveComponent,
    SDO.ItemList,
]

CHT_TERM_TYPES = {
    adlib_xpaths.MATERIAL_ITEM: [SDO.DefinedTerm, SDO.URL],
    adlib_xpaths.OBJECT_CATEGORY: [SDO.DefinedTerm],
    adlib_xpaths.ASSOCIATION_SUBJECT: [SDO.DefinedTerm, SDO.URL],
}

CHT_TERM_FIELD_MAPPING = {
    adlib_xpaths.MATERIAL_ITEM: SDO.material,
    adlib_xpaths.OBJECT_CATEGORY: SDO.genre,
    adlib_xpaths.ASSOCIATION_SUBJECT: SDO.additionalType,
} 

LOCATION_FIELDS = {
    adlib_xpaths.PRODUCTION_PLACE: [SDO.locationCreated, SDO.Place],
}

BASIC_MAPPING_NL = {
    adlib_xpaths.DESCRIPTION_TEXT: SDO.description,
    adlib_xpaths.OBJECT_NAME_ITEM: SDO.name,
    adlib_xpaths.DIMENSION_FREE: SDO.size,
    adlib_xpaths.OBJECT_NUMBER: SDO.identifier,
    adlib_xpaths.PRODUCTION_DATE_END: SDO.dateCreated,
}

BASIC_MAPPING = {
    adlib_xpaths.PRODUCTION_DATE_END: SDO.dateCreated,
}

RIGHTS_MAPPING = {
    adlib_xpaths.RIGHTS_HOLDER: SDO.copyrightHolder,
}

CREATOR_MAPPING = {
    adlib_xpaths.CREATOR_NAME: [SDO.name, Literal], 
    adlib_xpaths.RKDARTISTS: [SDO.sameAs, URIRef], 
    adlib_xpaths.CREATOR_DATE_OF_DEATH: [SDO.deathDate, Literal],
    adlib_xpaths.CREATOR_DATE_OF_BIRTH: [SDO.birthDate, Literal],
    adlib_xpaths.CREATOR_ROLE: [SDO.hasOccupation, Literal],
}

DIMENSION_MAPPING = {
    adlib_xpaths.DIMENSION_UNIT: SDO.unitText,
    adlib_xpaths.DIMENSION_VALUE: SDO.value,
}

REPRODUCTION_MAPPING = {
    adlib_xpaths.REPRODUCTION_REFERENCE: [SDO.associatedMedia, SDO.MediaObject, SDO.contentUrl, SDO.encodesCreativeWork]
}

PRODUCTION_MAPPING = {
    adlib_xpaths.PRODUCTION_DATE_END: SDO.dateCreated
}