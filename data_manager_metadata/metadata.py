"""Data Manager Metadata Class Definitions.
    Hints: https://pynative.com/make-python-class-json-serializable/
"""
import json
import datetime
import yaml
import jsonpickle
from abc import ABC, abstractmethod

_METADATA_VERSION: str = '0.0.1'
_ANNOTATION_VERSION: str = '0.0.1'


def metadata_version() -> str:
    return _METADATA_VERSION


def annotation_version() -> str:
    return _ANNOTATION_VERSION


def json_default(value):
    if isinstance(value, datetime.date):
        return value.isoformat()
    else:
        return value.__dict__


class Metadata:
    """Class Metadata

    Purpose: Defines a list of metadata dnd annotations that can be serialized and saved in a
    dataset.

    """
    name: str = ''
    description: str = ''
    created: datetime = 0
    last_updated: datetime = 0
    created_by: str = ''
    metadata_version: str = ''
    annotations: list = []

    def __init__(self, name: str, description: str, created_by: str, annotations: list):
        self.name = name
        self.description = description
        self.created = datetime.datetime.now()
        self.created_by = created_by
        self.metadata_version = metadata_version()
        self.annotations = annotations

    def add_annotation(self, annotation: object):
        """ Add a serialized annotation to the annotation list
        """
        self.annotations.append(annotation)
        self.last_updated = datetime.datetime.now()

    def remove_annotation(self, name: str):
        """ Remove an annotation from the annotation list
        """
        for annotation in self.annotations:
            if annotation.name == name:
                self.annotations.remove(annotation)
        self.last_updated = datetime.datetime.now()

    def get_annotation(self, name: str):
        """ Get an annotation from the annotation list identified by the name.
        """
        for annotation in self.annotations:
            if annotation.name == name:
                return annotation

    def to_json(self):
        """ Serialize class to JSON
        """
        return json.dumps(self, default=json_default)

    def to_pickle(self):
        return jsonpickle.encode(self)


class Annotation(ABC):
    """Class Annotation - Abstract Base Class to enable annotation functionality

    Purpose: Annotations can be added to Metadata. They are defined as classes to that they can
    have both fixed data and methods that work with the data.

    """
    type: str = ''
    name: str
    created: datetime = 0
    last_updated: datetime = 0
    annotation_version: str = ''

    @abstractmethod
    def __init__(self, annotation_type: str, name: str):
        self.type = annotation_type
        self.name = name
        self.created = datetime.datetime.now()
        self.annotation_version = annotation_version()

    def set_last_updated(self):
        self.last_updated = datetime.datetime.now()

    def to_json(self):
        """ Serialize class to JSON
        """
        return json.dumps(self, default=json_default)

    def to_pickle(self):
        return jsonpickle.encode(self)


class LabelAnnotation(Annotation):
    """Class LabelAnnotation

    Purpose: Object to create a simple label type of annotation to add to the metadata.

    """
    _type: str = 'label'
    label: str = ''
    value: str = ''

    def __init__(self, label: str, value: str, name: str = None):
        self.label = label
        self.value = value

        # default the name to the label if not present
        if not name:
            name = label
        super().__init__(self._type, name)

    def to_dict(self):
        return {"label": self.label, "value": self.value}


class FieldDescriptorAnnotation(Annotation):
    """Class FieldAnnotation

    Purpose: Object to add a Field Descriptor annotation to the metadata.

    """
    _type: str = 'field_descriptor'
    origin: str = ''
    description: str = ''
    fields: dict = {}

    def __init__(self, origin: str, description: str, name: str):
        self.origin = origin
        self.description = description
        super().__init__(self._type, name)

    def add_field(self, field_name: str, field_type: str, description: str):
        """ Add a field name to the fields dictionary with field_name as key and type/desc as
            properties.
        """
        self.fields[field_name] = {'type': field_type, 'description': description}
        super().set_last_updated()

    def remove_field(self, fieldname: str):
        """ Remove an annotation from the annotation list
        """
        del self.fields[fieldname]
        super().set_last_updated()

    def get_field(self, fieldname: str):
        """ Get an annotation from the annotation list identified by the name.
        """
        return self.fields[fieldname]

    def to_json(self):
        """ Serialize class to JSON
        """
        json_dict = {}
        json_dict['annotation'] = json.loads(super().to_json())
        json_dict['fields'] = self.fields

        return json.dumps(json_dict, default=json_default)


class ServiceExecutionAnnotation(FieldDescriptorAnnotation):
    """Class FieldAnnotation

    Purpose: Object to add a Field Descriptor annotation to the metadata.

    """
    _type: str = 'service_execution'
    service: str = ''
    service_version: str = ''
    service_user: str = ''
    parameters: dict = {}

    def __init__(self, service: str,
                 service_version: str,
                 service_user: str,
                 parameters: dict,
                 origin: str,
                 description: str,
                 name: str):
        self.service = service
        self.service_version = service_version
        self.service_user = service_user
        self.parameters = parameters
        super().__init__(origin, description, name)

    def parameters_to_yaml(self):
        return yaml.dump(self.parameters)


if __name__ == "__main__":
    print('Data Manager Metadata (v%s)', _METADATA_VERSION)
    print('Data Manager Annotation (v%s)', _ANNOTATION_VERSION)
