#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from urllib.request import urlopen
from xml.dom.minidom import parseString
from yaml import safe_dump
import sys
from re import sub
from os import environ


class ConfigurationChecker:
    def __init__(self):
        try:
            environ["TARGET_FILE_PATH"]
        except KeyError:
            print('There is no target file path in TARGET_FILE_PATH environment variable')
            sys.exit(2)
        try:
            environ["METADATA_SOURCE_URLS"]
        except KeyError:
            print('There is no metadata sources url in METADATA_SOURCE_URLS environment variable')
            sys.exit(2)


class MetadataHarvester:
    def __init__(self, url):
        filehandle = urlopen(url)
        self.xml = filehandle.read()
        filehandle.close()


class Parser:
    def __init__(self, xml):
        document_object = parseString(xml)
        self.parameters = dict()
        for entity_descriptor in document_object.getElementsByTagName("md:EntityDescriptor"):
            entity_id = entity_descriptor.attributes["entityID"].value
            contacts = []
            for contact_person_node in entity_descriptor.getElementsByTagName("md:ContactPerson"):
                contact_type = contact_person_node.attributes["contactType"].value
                contact = dict()
                contact["type"] = contact_type
                for xml_type, yaml_type in {
                        "md:EmailAddress": "email",
                        "md:GivenName": "surName",
                        "md:SurName": "surName"
                        }.items():
                    node = contact_person_node.getElementsByTagName(xml_type)
                    if node.length:
                        key = yaml_type
                        value = node[0].firstChild.nodeValue

                        # filter out ape from first place (avoid symfony service includeing)
                        value = sub("^@", '', value)

                        if key == "email":
                            value = sub('^mailto:', '', value)
                        contact[key] = value
                try:
                    contact["surName"]
                except KeyError:
                    contact["surName"] = "N/A"
                contacts.append(contact)
            self.parameters.update({entity_id: contacts})


class Exporter:
    def __init__(self, parameters, target_file_path):
        export = {"parameters": {"hexaa_service_entityids": parameters}}
        with open(target_file_path, 'w') as yaml_file:
            safe_dump(export, yaml_file, default_flow_style=False, allow_unicode=True, indent=4)
        # print(safe_dump(export, default_flow_style=False, allow_unicode=True))


if __name__ == "__main__":
    exporter_target_file_path = environ["TARGET_FILE_PATH"]
    metadata_sources = environ["METADATA_SOURCE_URLS"].split(",")
    if len(metadata_sources) < 1:
        print('There is no metadata sources url in METADATA_SOURCE_URLS environment variable')
        sys.exit(2)

    exporter_parameters = dict()
    for metadata_source in metadata_sources:
        mh = MetadataHarvester(metadata_source.strip())
        parser = Parser(mh.xml)
        exporter_parameters.update(parser.parameters)

    Exporter(exporter_parameters, exporter_target_file_path)
