"""Data Manager Metadata Class Definitions.

"""
import json
import datetime

_METADATA_VERSION: str = '0.0.0'


def version() -> str:
    return _METADATA_VERSION


class Metadata:
    """Class Metadata

    Purpose: Defines a list of metadata dnd annotations that can be serialized and saved in a
    dataset.

    """
    metadata: json = {}
    annotations: list = []
    pass

    def to_json(self):
        """ Serialize class to JSON
        """
        pass


class Annotation:
    """Class Annotation

    Purpose: Annotations can be added to Metadata. They are defined as classes to that they can
    have both fixed data and methods that work with the data.

    """
    type: str = ''
    created: datetime = 0
    name: str
    pass

    def to_json(self):
        """ Serialize class to JSON
        """
        pass


class LabelAnnotation(Annotation):
    """Class LabelAnnotation

    Purpose: Object to .

    """
    label: str = ''
    value: str = ''
    pass


class TagAnnotation(Annotation):
    """Class TagAnnotation
    https://training.galaxyproject.org/training-material/topics/galaxy-interface/tutorials/name-tags/tutorial.html

    Purpose: Object to .

    """
    pass


if __name__ == "__main__":
    print('Data Manager Metadata (v%s)', _METADATA_VERSION)
