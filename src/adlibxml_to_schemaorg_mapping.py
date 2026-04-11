import adlib_xpaths
from rdflib.namespace import SDO

MAPPING = {
    adlib_xpaths.DESCRIPTION_TEXT: SDO.description,
    adlib_xpaths.MATERIAL_ITEM: SDO.material,
    adlib_xpaths.OBJECT_NAME_ITEM: SDO.name,
}