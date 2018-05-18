#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib import urlopen
from xml.dom.minidom import parseString
from yaml import safe_dump
import sys
from re import sub
from os import environ

class MetadataHarvester:
    def __init__(self, url):
        filehandle = urlopen(url)
        self.xml = filehandle.read()
        filehandle.close()


class Parser():
    def __init__(self, xml):
        document_object = parseString(xml)
        self.parameters = []
        for entity_descriptor in document_object.getElementsByTagName("md:EntityDescriptor"):
            entity_id = entity_descriptor.attributes["entityID"].value
            contacts = []
            for contact_person_node in entity_descriptor.getElementsByTagName("md:ContactPerson"):
                contact_type = contact_person_node.attributes["contactType"].value.encode('utf-8')
                contact = {}
                contact["type"] = contact_type
                for type in [{"md:EmailAddress": "email"}, {"md:GivenName": "surName"}, {"md:SurName": "surName"}]:
                    node = contact_person_node.getElementsByTagName(type.keys()[0])
                    if node.length:
                        key = type.values()[0].encode('utf-8')
                        value = node[0].firstChild.nodeValue.encode('utf-8')
                        if key == "email":
                            value = sub('^mailto:', '', value)
                        contact[key] = value
                contacts.append(contact)
            self.parameters.append({entity_id.encode('utf-8'): contacts})


class Exporter():
    def __init__(self, parameters, target_file_path):
        export = {"parameters": {"hexaa_service_entityids": parameters}}
        with open(target_file_path, 'w') as yaml_file:
            safe_dump(export, yaml_file, default_flow_style=False, allow_unicode=True)


class ConfigurationChecker():
    def __init__(self):
        try:
            environ["TARGET_FILE_PATH"]
        except KeyError:
            print 'There is no target file path in TARGET_FILE_PATH environment variable'
            sys.exit(2)
        try:
            environ["METADATA_SOURCE_URLS"]
        except KeyError:
            print 'There is no metadata sources url in METADATA_SOURCE_URLS environment variable'
            sys.exit(2)


if __name__ == "__main__":
    target_file_path = environ["TARGET_FILE_PATH"]
    metadata_sources = environ["METADATA_SOURCE_URLS"].split(",")
    if len(metadata_sources) < 1:
        print 'There is no metadata sources url in METADATA_SOURCE_URLS environment variable'
        sys.exit(2)

    parameters = []
    for metadata_source in metadata_sources:
        mh = MetadataHarvester(metadata_source.strip())
        parser = Parser(mh.xml)
        parameters.extend(parser.parameters)

    Exporter(parameters, target_file_path)