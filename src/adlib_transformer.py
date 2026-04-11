import logging
import xml.etree.ElementTree as ET
import adlib_xpaths as xpath
import adlib_tags as tags
import lod_mapper as lmap

logger = logging.getLogger(__name__)
path = 'data/output/rubenpriref24099.adlib.xml'

# https://adlibug.nl/2014/09/17/how-to-create-a-full-list-of-tags-using-xml-and-xsl/

def get_text_from_xpath_safe(tree: ET, target_xpath: str) -> str:
    t_elem = tree.find(target_xpath)
    if t_elem is not None and t_elem.text:
        return t_elem.text

def parse_tree(tree: ET) -> dict[str]:
    parsed_record = {}
    
    for index, asubj in enumerate(tree.findall(xpath.ASSOCIATED_SUBJECT)):
        parsed_record[xpath.ASSOCIATION_SUBJECT + '/' + str(index)] = asubj.find(tags.ASSOCIATION_SUBJECT).text
        parsed_record[xpath.ASSOCIATION_SUBJECT_TYPE + '/' + str(index)] = asubj.find(tags.ASSOCIATION_SUBJECT_TYPE)[0].text

    parsed_record[xpath.DESCRIPTION_TEXT] = get_text_from_xpath_safe(tree, xpath.DESCRIPTION_TEXT)
    parsed_record[xpath.INSCRIPTION_DESCRIPTION] = get_text_from_xpath_safe(tree, xpath.INSCRIPTION_DESCRIPTION)
    parsed_record[xpath.MATERIAL_ITEM] = get_text_from_xpath_safe(tree, xpath.MATERIAL_ITEM)
    parsed_record[xpath.OBJECT_NAME_ITEM] = get_text_from_xpath_safe(tree, xpath.OBJECT_NAME_ITEM)
    parsed_record[xpath.CREATOR_NAME] = get_text_from_xpath_safe(tree, xpath.CREATOR_NAME)
    parsed_record[xpath.CREATOR_DATE_OF_BIRTH] = get_text_from_xpath_safe(tree, xpath.CREATOR_DATE_OF_BIRTH)
    parsed_record[xpath.CREATOR_DATE_OF_DEATH] = get_text_from_xpath_safe(tree, xpath.CREATOR_DATE_OF_DEATH)
    parsed_record[xpath.PRODUCTION_DATE_END] = get_text_from_xpath_safe(tree, xpath.PRODUCTION_DATE_END)
    parsed_record[xpath.PRODUCTION_DATE_START] = get_text_from_xpath_safe(tree, xpath.PRODUCTION_DATE_START)

    for index, rr in enumerate(tree.findall(xpath.REPRODUCTION_REFERENCE)):
        parsed_record[xpath.REPRODUCTION_REFERENCE + '/' + str(index)] = rr.text  
    
    parsed_record[xpath.RIGHTS_ASSIGNED_VALUE] = get_text_from_xpath_safe(tree, xpath.RIGHTS_ASSIGNED_VALUE)
    parsed_record[xpath.RIGHTS_HOLDER] = get_text_from_xpath_safe(tree, xpath.RIGHTS_HOLDER)
    parsed_record[xpath.RIGHTS_NOTES] = get_text_from_xpath_safe(tree, xpath.RIGHTS_NOTES)
    parsed_record[xpath.RIGHTS_TYPE] = get_text_from_xpath_safe(tree, xpath.RIGHTS_TYPE)

    return dict(filter(lambda item: item[1] is not None, parsed_record.items()))

def parse_path(path: str) -> dict[str]:
    etree = ET.parse(path)    
    parsed_record = parse_tree(etree)
    return parsed_record
