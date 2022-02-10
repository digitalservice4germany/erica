import os

from xml.dom import minidom

_INSTANCES_FOLDER = os.path.join('erica', 'instances')
_BLUEPRINT_FOLDER = os.path.join(_INSTANCES_FOLDER, 'blueprint')


def pretty_xml_string(xml_string):
    dom_string = minidom.parseString(xml_string).toprettyxml(indent=" "*4)
    return '\n'.join([s for s in dom_string.splitlines() if s.strip()])  # remove empty lines


def generate_dummy_error_response():
    error_response = {"errorCode": -1,
                      "errorMessage": "API resource not yet implemented."
                      }
    return error_response
