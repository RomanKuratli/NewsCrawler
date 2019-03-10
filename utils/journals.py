"""
This module loads the journal settings from /static/journals/journals.xml and does also schema validation
"""
import xml.etree.ElementTree as ET
from importlib import import_module
from os import path
import xmlschema
from utils.settings import APP_JOURNALS
import logging
logger = logging.getLogger(__name__)




def make_dict(path):
    journals_dict = {}
    for journal_tag in ET.parse(path).getroot():
        journal_dict = {}
        for elem in journal_tag:
            tag = elem.tag
            if tag in ("Display", "BaseLink"): # just copy into the dict
                journal_dict[tag] = elem.text
            elif tag in ("Crawler", "Indexer"): # has to be turned into a function
                mod_name, fun_name = elem.text.split(".", 2)
                mod = import_module(f"{tag.lower()}s.{mod_name}")
                fun = getattr(mod, fun_name)
                journal_dict[tag] = fun
            elif tag == "Sections": # generate a list with the <Section> tags
                journal_dict[tag] = [section_tag.text for section_tag in elem]
        journals_dict[journal_tag.attrib["coll"]] = journal_dict
    return journals_dict


xml_path = path.join(APP_JOURNALS, "journals.xml")
xsd_path = path.join(APP_JOURNALS, "journals.xsd")
xsd = xmlschema.XMLSchema(xsd_path)
assert xsd.is_valid(xml_path), f"XML {xml_path} is not valid according to {xsd_path}"
logger.info(f"Configuration file {xml_path} is valid")
JOURNALS = make_dict(xml_path)
