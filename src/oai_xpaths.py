ADLIBXML = './adlibXML'
RECORDLIST = './adlibXML/recordList'
RECORD = './adlibXML/recordList/record'

ASSOCIATED_SUBJECT = './/Associated_subject'
ASSOCIATION_SUBJECT = './/association.subject'
ASSOCIATION_SUBJECT_TYPE = './/association.subject.type'
ASSOCIATION_SUBJECT_TYPE_VALUE = './/association.subject.type/value'
ASSOCIATION_SUBJECT_SRC_URI = './/association.subject/Source/source.number'
ASSOCIATION_SUBJECT_TERM = './/association.subject/term'

DIMENSION = './/Dimension'
DIMENSION_FREE = './/dimension.free'
DIMENSION_PART = './/dimension.part'
DIMENSION_TYPE = './/dimension.type'
DIMENSION_UNIT = './/dimension.unit'
DIMENSION_VALUE = './/dimension.value'

CONDITION = './/Condition'
CONDITION_TEXT = './/condition'
CONDITION_CHECK_NAME = './/condition.check.name'
CONDITION_DATE = './/condition.date'
CONDITION_NOTES = './/condition.notes'

VALUE = './/value'
TERM_NAME = './/term'
TERM_URI = './/Source/source.number'

DESCRIPTION = './/Description'
DESCRIPTION_TEXT = './/Description/description'

INSCRIPTION = './/Inscription'
INSCRIPTION_DESCRIPTION = './/Inscription/inscription.description'

MATERIAL = './/Material'
MATERIAL_ITEM = './/Material/material'
MATERIAL_PART = './/Material/material.part'
MATERIAL_SRC_URI = './/Material/material/Source/source.number'
MATERIAL_TERM = './/Material/material/term'


OBJECT_NAME = './/Object_name'
OBJECT_NAME_ITEM = './/Object_name/object_name/term'

CREATOR = './/Production/creator'
CREATOR_PRIREF = './/Production/creator/priref'
CREATOR_NAME = './/Production/creator/name'
CREATOR_BIRTHPLACE = './/Production/creator/birth.place'
CREATOR_BIRTHPLACE_URI = './/Production/creator/name'

CREATOR_DATE_OF_BIRTH = './/creator.date_of_birth'
CREATOR_DATE_OF_DEATH = './/creator.date_of_death'
CREATOR_ROLE = './/creator.role'
RKDARTISTS = './/Production/creator/Source/source.number'


# Binnen één Production-groep (paden relatief aan het Production-element). In Adlib staat elke maker in een eigen
# Production-groep; rol, geboortedatum en sterfdatum staan naast de maker in diezelfde groep.
GROUP_CREATOR = './creator'
GROUP_CREATOR_PRIREF = './creator/priref'
GROUP_CREATOR_NAME = './creator/name'
GROUP_CREATOR_BIRTHPLACE = './creator/birth.place'
GROUP_CREATOR_RKD = './creator/Source/source.number'
GROUP_CREATOR_DATE_OF_BIRTH = './creator.date_of_birth'
GROUP_CREATOR_DATE_OF_DEATH = './creator.date_of_death'
GROUP_CREATOR_ROLE = './creator.role'

ALTERNATIVE_NUMBER = './/Alternative_number'
ALTERNATIVE_NUMBER_VALUE = './alternative_number'
ALTERNATIVE_NUMBER_TYPE = './alternative_number.type'

# Thema's: alleen de benoemde term, niet de bijbehorende vrije toelichting
THEMA_TERMS = [
    './/Thema/content.motif.general',
    './/Thema/content.motif.specific',
    './/Thema_wat/theme.subject.what',
    './/Thema_wie/content.person.name',
    './/Thema_waar/theme.subject.where',
]

PRODUCTION = './/Production'
PRODUCTION_NOTES = './/production.notes'
PRODUCTION_PLACE = './/production.place'
PRODUCTION_PLACE_SRC_TERM = './/production.place/term'
PRODUCTION_PLACE_SRC_URI = './/production.place/Source/source.number'
PRODUCTION_DATE = './/Production_date'
PRODUCTION_DATE_END = './/production.date.end'
PRODUCTION_DATE_START = './/production.date.start'

REPRODUCTION = './/Reproduction'
REPRODUCTION_REFERENCE = './/reproduction.reference'

RIGHTS = './/Rights'
RIGHTS_ASSIGNED = './/rights.assigned'
RIGHTS_ASSIGNED_VALUE = './/rights.assigned/value'
RIGHTS_HOLDER = './/rights.holder'
RIGHTS_NOTES = './/rights.notes'
RIGHTS_TYPE = './/rights.type'

#Alternative_number
#alternative_number
#alternative_number.type

TITLE = './/Title'
TITLE_TEXT = './/Title/title'

INSTITUTION_NAME = './/institution.name'
NUMBER_OF_PARTS = './/number_of_parts'

OBJECT_CATEGORY = './/object_category'
OBJECT_CATEGORY_TERM = './/object_category/term'
OBJECT_CATEGORY_SRC_URI = './/object_category/Source/source.number'
TECHNIQUE_ITEM = './/Technique/technique'
TECHNIQUE = './/Technique/technique/term'
TECHNIQUE_URI = './/Technique/technique/Source/source.number'

# Objectnaam als term (met Getty AAT-URI); OBJECT_NAME_ITEM hierboven is alleen de tekst voor schema:alternateName
OBJECT_NAME_TERM_ITEM = './/Object_name/object_name'

# Verwijzingen (URI's) naar elders: digitale bron (RKDimages, Collectie Nederland, handle), advies Restitutiecommissie,
# en gerelateerde objecten (objectnummer, wordt een beeldbank-adres)
DIGITAL_REFERENCE = './/Digital_reference/digital_reference'
RESTITUTION_REFERENCE = './/Restitution_status/restitution.status.reference'
RELATED_OBJECT_REFERENCE = './/Related_object/related_object.reference'

OBJECT_NUMBER = './/object_number'

PART = './/part'
PRIREF = './priref'
MODIFICATION = './/modification'

RECORD_TYPE = './/record_type'

USER_CODE = './/user_code'

DIAGNOSTIC = './adlibXML/diagnostic'
HITS = './adlibXML/diagnostic/hits'
XMLTYPE = './adlibXML/diagnostic/xmltype'
HITS_ON_DISPLAY = './adlibXML/diagnostic/hits_on_display'
SEARCH = './adlibXML/diagnostic/search'
FIRST_ITEM = './adlibXML/diagnostic/first_item'
FORWARD = './adlibXML/diagnostic/forward'
BACKWARD = './adlibXML/diagnostic/backward'
LIMIT = './adlibXML/diagnostic/limit'
DBNAME = './adlibXML/diagnostic/dbname'
DSNAME = './adlibXML/diagnostic/dsname'

CGISTRING = './adlibXML/diagnostic/cgistring'
PARAM = './adlibXML/diagnostic/cgistring/param'

LINK_RESOLVE_TIME = './adlibXML/diagnostic/link_resolve_time'