#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from urllib import request
from xml.dom.minidom import parseString
import sys
from re import sub
from os import environ
import logging

from time import sleep

from yaml import safe_dump


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
        filehandle = request.urlopen(url)
        logging.debug('Return code from %s: %s', url, filehandle.getcode())
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
                        try:
                            value = node[0].firstChild.nodeValue
                        except AttributeError:
                            logging.info('%s attribute is missing for'
                                         ' the %s contact of %s. Skipping it.',
                                         xml_type, contact_type, entity_id)
                            continue

                        # filter out ape from first place (avoid symfony service including)
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
    logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

    exporter_target_file_path = environ["TARGET_FILE_PATH"]
    metadata_sources = environ["METADATA_SOURCE_URLS"].split(",")

    repeat = False
    try:
        interval = int(environ['UPDATE_INTERVAL_MINUTES'])
        repeat = True
    except ValueError:
        print('The UPDATE_INTERVAL_MINUTES value is not an integer.')
        sys.exit(2)
    except KeyError:
        pass

    if len(metadata_sources) < 1:
        print('There is no metadata sources url in METADATA_SOURCE_URLS environment variable')
        sys.exit(2)

    while True:
        exporter_parameters = dict()
        for metadata_source in metadata_sources:
            try:
                mh = MetadataHarvester(metadata_source.strip())
                parser = Parser(mh.xml)
                exporter_parameters.update(parser.parameters)
                logging.info(f'Successfuly fetched metadata from {metadata_source}')
            except (request.URLError, AttributeError) as err:
                logging.exception('Could not fetch metadata from %s', metadata_source)


        try:
            Exporter(exporter_parameters, exporter_target_file_path)
        except PermissionError:
            logging.exception('Could not write SP metadata to %s', exporter_target_file_path)

        if not repeat:
            break

        sleep(interval * 60)
