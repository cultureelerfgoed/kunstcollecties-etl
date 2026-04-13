import adlib_xpaths
from rdflib.namespace import SDO

BASIC_MAPPING = {
    adlib_xpaths.DESCRIPTION_TEXT: SDO.description,
    adlib_xpaths.MATERIAL_ITEM: SDO.material,
    adlib_xpaths.OBJECT_NAME_ITEM: SDO.name,
    adlib_xpaths.DIMENSION_FREE: SDO.size,
}

RIGHTS_MAPPING = {
    adlib_xpaths.RIGHTS_HOLDER: SDO.copyrightHolder,
}

CREATOR_MAPPING = {
    adlib_xpaths.CREATOR_NAME: SDO.name, 
    adlib_xpaths.RKDARTISTS: SDO.sameAs, 
    adlib_xpaths.CREATOR_DATE_OF_DEATH: SDO.deathDate,
    adlib_xpaths.CREATOR_DATE_OF_BIRTH: SDO.birthDate, 
    adlib_xpaths.CREATOR_ROLE: SDO.additionalType,
}

DIMENSION_MAPPING = {
    adlib_xpaths.DIMENSION_UNIT: SDO.unitText,
    adlib_xpaths.DIMENSION_VALUE: SDO.value,
}