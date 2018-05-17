#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib import urlopen
from xml.dom.minidom import parseString
from yaml import dump
import sys
from re import sub


class MetadataHarvester:
    def __init__(self, url):
        filehandle = urlopen(url)
        self.xml = filehandle.read()
        filehandle.close()


class Parser():
    def __init__(self, xml):
        document_object = parseString(xml)
        self.parameters = {}
        for entity_descriptor in document_object.getElementsByTagName("md:EntityDescriptor"):
            entity_id = entity_descriptor.attributes["entityID"].value
            contacts = []
            for contact_person_node in entity_descriptor.getElementsByTagName("md:ContactPerson"):
                contact_type = contact_person_node.attributes["contactType"].value.encode('utf-8')
                contact = {}
                contact["type"] = contact_type
                for type in [{"md:EmailAddress": "email"}, {"md:GivenName": "givenName"}, {"md:SurName": "surName"}]:
                    node = contact_person_node.getElementsByTagName(type.keys()[0])
                    if node.length:
                        key = type.values()[0].encode('utf-8')
                        value = node[0].firstChild.nodeValue.encode('utf-8')
                        if key == "email":
                            value = sub('^mailto:', '', value)
                        contact[key] = value
                contacts.append(contact)
            self.parameters[entity_id.encode('utf-8')] = contacts


class Exporter():
    def __init__(self, parameters):
        export = {"parameters": {"hexaa_service_entityids": parameters}}
        print dump(export, default_flow_style=False)


if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) < 2:
        print 'hexaa-service-entityids-generator.py <space separated metadatasource_urls>'
        sys.exit(2)
    del arguments[0]
    metadata_sources = arguments

    parameters = []

    for metadata_source in metadata_sources:
        mh = MetadataHarvester(metadata_source)
        parser = Parser(mh.xml)
        parameters.append(parser.parameters)

    Exporter(parameters)
