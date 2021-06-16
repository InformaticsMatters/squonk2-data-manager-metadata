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
    dataset_name: str = ''
    description: str = ''
    created: datetime = 0
    last_updated: datetime = 0
    created_by: str = ''
    metadata_version: str = ''
    annotations: list = []

    def __init__(self, dataset_name: str, description: str, created_by: str, annotations: list):
        assert dataset_name
        assert description
        assert created_by

        self.dataset_name = dataset_name
        self.description = description
        self.created = datetime.datetime.utcnow()
        self.created_by = created_by
        self.metadata_version = metadata_version()
        self.annotations = annotations

    def get_dataset_name(self):
        return self.dataset_name

    def get_description(self):
        return self.description

    def get_created_by(self):
        return self.created_by

    def get_metadata_version(self):
        return self.metadata_version

    def add_annotation(self, annotation: object):
        """ Add a serialized annotation to the annotation list
        """
        self.annotations.append(annotation)
        self.last_updated = datetime.datetime.utcnow()

    def remove_annotation(self, name: str):
        """ Remove an annotation from the annotation list
        """
        for annotation in self.annotations:
            if annotation.name == name:
                self.annotations.remove(annotation)
        self.last_updated = datetime.datetime.utcnow()

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

    def to_dict(self):
        """Return principle data items in the form of a dictionary
        """
        return {"dataset_name": self.dataset_name,
                "description": self.description,
                "created_by": self.created_by,
                "annotations": self.annotations}


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
        assert annotation_type

        self.type = annotation_type
        self.name = name
        self.created = datetime.datetime.utcnow()
        self.annotation_version = annotation_version()

    def set_last_updated(self):
        self.last_updated = datetime.datetime.utcnow()

    def set_name(self, name: str):
        self.name = name

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def to_dict(self):
        """Return principle data items in the form of a dictionary
        """
        return {"type": self.type,
                "name": self.name}

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
        assert label
        self.label = label
        self.value = value

        # default the name to the label if not present
        if not name:
            name = label
        super().__init__(self._type, name)

    def to_dict(self):
        """Return principle data items in the form of a dictionary
        """
        return {"annotation": super().to_dict(), "label": self.label,
                "value": self.value}


class FieldDescriptorAnnotation(Annotation):
    """Class FieldAnnotation

    Purpose: Object to add a Field Descriptor annotation to the metadata.

    """
    _type: str = 'field_descriptor'
    origin: str = ''
    description: str = ''
    fields: dict = {}

    def __init__(self, origin: str, description: str, fields: dict, name: str):
        self.origin = origin
        self.description = description
        self.fields = fields
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
        json_dict = {'annotation': json.loads(super().to_json()), 'fields': self.fields}
        return json.dumps(json_dict, default=json_default)

    def to_dict(self):
        """Return principle data items in the form of a dictionary
        """
        return {"annotation": super().to_dict(), "origin": self.origin,
                "description": self.description, "fields": self.fields}


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
                 fields: dict,
                 name: str):
        assert service

        self.service = service
        self.service_version = service_version
        self.service_user = service_user
        self.parameters = parameters
        super().__init__(origin, description, fields, name)

    def parameters_to_yaml(self):
        return yaml.dump(self.parameters)

    def to_dict(self):
        """Return principle data items in the form of a dictionary
        """
        return {"field_descriptor": super().to_dict(),
                "service": self.service, "service_version": self.service_version,
                "service_user": self.service_user,
                "parameters": self.parameters}


if __name__ == "__main__":
    print('Data Manager Metadata (v%s)', _METADATA_VERSION)
    print('Data Manager Annotation (v%s)', _ANNOTATION_VERSION)
