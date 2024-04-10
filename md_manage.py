#!/usr/bin/env python

"""md_manage.py

Python module extension to create annotations via the command line.

Examples:
    python md_manage.py -h
    python md_manage.py lb -h
    python md_manage.py fd -h
    python md_manage.py se -h
    - help functions.

    python md_manage.py lb 'label' -lv='blob' -af=test/output
    - create a label annotation in an annotations.json file placed in test/output. Running the
    command again will create a second annotation in the same file (i.e. a list of two).

    python md_manage.py fd -fo='squonk2-job' -fp='minimizedAffinity,number,Binding affinity \
                        predicted by smina using the vinardo scoring function,true,true' \
                        -fd='Run smina docking' -af=test/output
    - create a FieldsDescriptorAnnotation in an annotations.json file placed in test/output.

    python md_manage.py se -su=bob -sys='run-smina' -sy='test/input/virtual-screening.yaml' \
                        -sp param1=val1 param2=val2 -fo='squonk2-job' \
                        -fp='minimizedAffinity,number,Binding affinity predicted,true,true' \
                        -fd='Run smina docking' -af=test/output
    - create a service execution annotation in an annotations.json file placed in test/output.


See the README for more details.

"""

import argparse
import os
import sys
import json
from yaml import safe_load
from data_manager_metadata.metadata import (
    FIELD_DICT,
    get_annotation_filename,
    Metadata,
    LabelAnnotation,
    FieldsDescriptorAnnotation,
    ServiceExecutionAnnotation,
)


def add_label_annotation_args(c_parser):
    """Add arguments for the label annotation formatter"""
    # This is common to all annotations should be first
    c_parser.add_argument(
        'filepath',
        type=str,
        help='Filepath to a (results) file that will have an annotations file. '
        'associated with it. If the file exists then annotations will be'
        ' appended - Required',
    )
    c_parser.add_argument('label', type=str, help='Label, required')
    c_parser.add_argument(
        '-lv', '--value', type=str, help='Value to attach the label, optional'
    )
    c_parser.add_argument(
        '--make-inactive',
        action='store_false',
        help='When set, this makes the ' 'label inactive',
    )

    c_parser.set_defaults(func=create_label_annotation)


def add_fields_descriptor_annotation_args(c_parser):
    """Add arguments for the fields descriptor annotation formatter"""
    # This is common to all annotations should be first
    c_parser.add_argument(
        'filepath',
        type=str,
        help='Filepath to a (results) file that will have an annotations file. '
        'associated with it. If the file exists then annotations will be'
        ' appended - Required',
    )
    c_parser.add_argument('-fo', '--origin', type=str, help='Origin of Dataset')
    c_parser.add_argument(
        '-fd', '--description', type=str, help='Description of Dataset'
    )
    c_parser.add_argument(
        '-fp',
        '--add_field_property',
        type=str,
        help='Add a field in comma separated form in order: name,type,'
        'description,required,active,semantic_ref. Fields: required, active '
        'and semantic-ref are optional ',
    )

    c_parser.set_defaults(func=create_fields_descriptor_annotation)


def add_service_execution_annotation_args(c_parser):
    """Add arguments for the service_execution annotation formatter"""
    c_parser.add_argument(
        '-su',
        '--service_user',
        type=str,
        help='User initiating the service. Required input',
    )
    c_parser.add_argument(
        '-sy',
        '--service_yaml_file',
        type=str,
        help='Route to yaml file containing service definition',
    )
    c_parser.add_argument(
        '-sys',
        '--service_yaml_section',
        type=str,
        help='Section in yaml file containing service definition details',
    )
    c_parser.add_argument(
        '-s',
        '--service',
        type=str,
        help='Name of the service being performed. Required if yaml file '
        'not present. If yaml file present, will overwrite value',
    )
    c_parser.add_argument(
        '-sv',
        '--service_version',
        type=str,
        help='Version of the service being performed. Required if yaml file '
        'not present. If yaml file present, will overwrite value',
    )
    c_parser.add_argument(
        '-sn',
        '--service_name',
        type=str,
        help='Name of service. Required if yaml file '
        'not present. If yaml file present, will overwrite value',
    )
    c_parser.add_argument(
        '-sr',
        '--service_ref',
        type=str,
        help='URL reference to documentation for service. Required if yaml file '
        'not present. If yaml file present, will overwrite value',
    )
    c_parser.add_argument(
        "-sp",
        '--service_parameters',
        metavar="KEY=VALUE",
        nargs='+',
        help="Add a number of key-value pairs containing service parameters "
        "(do not put spaces before or after the = sign). "
        "If a value contains spaces, you should define "
        "it with double quotes: "
        'foo="this is a sentence". Note that '
        "values are always treated as strings.",
    )
    # filename is provided implicitly by the FieldsDescriptor

    c_parser.set_defaults(func=create_service_execution_annotation)


def create_label_annotation(c_args):
    """Add a label annotation to the annotation json file"""
    return LabelAnnotation(c_args.label, c_args.value, c_args.make_inactive)


def _create_field_dict(fields: str):
    """Takes an list of fields in a string, unpacks and returns in a dictionary"""

    field_dict: dict = {}
    # fields are of the form: name: (type,description,required,semantic-type)
    prop_list = fields.split(',')
    name = prop_list[0]
    field_dict[name] = FIELD_DICT
    field_dict[name]['type'] = prop_list[1]
    field_dict[name]['description'] = prop_list[2]
    if len(prop_list) > 3:
        field_dict[name]['required'] = prop_list[3]
    if len(prop_list) > 4:
        field_dict[name]['active'] = prop_list[4]
    if len(prop_list) > 5:
        field_dict[name]['semantic_type'] = prop_list[5]
    return field_dict


def create_fields_descriptor_annotation(c_args):
    """Add a FieldsDescriptor annotation to the annotation json file"""
    field_dict: dict = {}

    if c_args.add_field_property:
        field_dict = _create_field_dict(c_args.add_field_property)

    return FieldsDescriptorAnnotation(c_args.origin, c_args.description, field_dict)


def _params_from_file(filename: str, section: str, param_dict: dict):
    """Parameters can be added from a supplied yaml file.

    The yaml file has to follow the naming convention used in the virtual screening repo.

    """

    if not os.path.isfile(filename):
        print('Yaml file does not exist in this location')
        sys.exit(1)

    with open(filename, 'rt', encoding='utf-8') as yaml_file:
        yaml_dict = safe_load(yaml_file)
        service_dict = yaml_dict['jobs'][section]

        param_dict['service'] = section
        param_dict['service_version'] = service_dict['version']
        param_dict['service_name'] = service_dict['name']

        # This is required in the annotation, so it should either be a required parameter or
        # added to the yaml.
        param_dict['service_ref'] = 'tba'
        param_dict['service_parameters'] = {
            'container_image': service_dict['image'],
            'container-command': service_dict['command'],
        }

    return param_dict


def _parse_parameter(param: str):
    """
    Parse a key, value pair, separated by '='
    On the command line (argparse) a parameter looks like:
        param=value
    or
        param="value"
    """

    items = param.split('=')
    key = items[0].strip()  # we remove blanks around keys, as is logical
    if len(items) > 1:
        # rejoin the rest:
        value = '='.join(items[1:])
    return (key, value)


def _params_from_line(service_parameters: list, param_dict: dict):
    """Parameters can be added in the command line in the form of key/value pairs

    The parameters are provided in a list that must be unpacked and added to the dictionary.
    The is of form: ['param1=val1', 'param2=val2']

    """

    for param in service_parameters:
        key, value = _parse_parameter(param)
        param_dict['service_parameters'][key] = value

    return param_dict


def create_service_execution_annotation(c_args):
    """Add a ServiceExecution annotation to the annotation json file"""
    field_dict: dict = ()
    param_dict: dict = {
        'service': c_args.service,
        'service_version': c_args.service_version,
        'service_user': c_args.service_user,
        'service_name': c_args.service_name,
        'service_ref': c_args.service_ref,
        'service_parameters': {},
        'origin': c_args.origin,
        'description': c_args.description,
        'fields': field_dict,
    }

    if c_args.add_field_property:
        field_dict = _create_field_dict(c_args.add_field_property)

    param_dict['fields'] = field_dict

    if c_args.service_yaml_file:
        param_dict = _params_from_file(
            c_args.service_yaml_file, c_args.service_yaml_section, param_dict
        )

    if c_args.service_parameters:
        param_dict = _params_from_line(c_args.service_parameters, param_dict)

    assert param_dict['service']
    assert param_dict['service_version']
    assert param_dict['service_user']
    assert param_dict['service_name']

    # This should ultimately be in the yaml file I think..
    assert param_dict['service_ref']

    return ServiceExecutionAnnotation(**param_dict)


if __name__ == '__main__':
    # Add an annotation to the annotation json file using the given parameters
    #
    # parameters are specific to the requested annotation.
    # A filepath for an annotations file can be optionally provided.
    # If the annotations file already exists, then the annotation will be added to it
    # in the form of an array.
    parser = argparse.ArgumentParser('Metadata Annotation Generator')
    subparsers = parser.add_subparsers(help='Please choose an annotation type')

    # Parser for Label Annotation
    parser_lb = subparsers.add_parser('lb', help='LabelAnnotation')
    add_label_annotation_args(parser_lb)

    # Parser for the Field Descriptor Annotation
    parser_fd = subparsers.add_parser('fd', help='FieldsDescriptorAnnotation')
    add_fields_descriptor_annotation_args(parser_fd)

    # Parser for the Service Execution Annotation (includes Field Descriptor
    parser_se = subparsers.add_parser('se', help='ServiceExecutionAnnotation')
    add_fields_descriptor_annotation_args(parser_se)
    add_service_execution_annotation_args(parser_se)

    args = parser.parse_args()
    assert args.filepath
    file_name = os.path.basename(args.filepath)
    file_dir = os.path.dirname(args.filepath)

    annotations_filename = get_annotation_filename(file_name)

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    anno_file = os.path.join(file_dir, annotations_filename)

    # Create a metadata class to act as a holder for annotations
    meta_holder = Metadata('dm', 'dm', 'dm', 'dm')

    if os.path.isfile(anno_file):
        # Annotations File already exists - import any annotations and add to the holder
        with open(anno_file, 'rt', encoding='utf-8') as existing_annotations:
            meta_holder.add_annotations(existing_annotations.read())

    # Create the new annotation and add to the list
    anno = args.func(args)
    meta_holder.add_annotation(anno)

    # Recreate output and write the list of annotations to it.
    out_file = open(anno_file, "w", encoding="utf-8")
    json.dump(meta_holder.get_annotations_dict(), out_file)
