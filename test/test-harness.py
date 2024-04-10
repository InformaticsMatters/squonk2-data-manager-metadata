# Test harness for temporary tests
import unittest
import json
from data_manager_metadata.metadata import (Metadata,
                                            LabelAnnotation,
                                            FieldsDescriptorAnnotation,
                                            ServiceExecutionAnnotation)

from data_manager_metadata.annotation_utils import est_schema_field_type
from data_manager_metadata.exceptions import (ANNOTATION_ERRORS,
                                              AnnotationValidationError)

class MyTestCase(unittest.TestCase):

    metadata = Metadata('test', '0000-1111', '', 'Bob')

    def test_01_metadata(self):
        print ('1.1 Metadata')
        results_metadata = {'dataset_name': 'test', 'dataset_uuid': '0000-1111', 'description': '',
                            'created_by': 'Bob', 'annotations': []}
        self.assertEqual(self.metadata.get_dataset_name(), results_metadata['dataset_name'])
        self.assertEqual(self.metadata.get_dataset_uuid(), results_metadata['dataset_uuid'])
        self.assertEqual(self.metadata.get_description(), results_metadata['description'])
        self.assertEqual(self.metadata.get_created_by(), results_metadata['created_by'])
        self.assertEqual(self.metadata.get_metadata_version(), '0.0.1')
        print('\nTest 1.1 ok')

        print ('1.2. Metadata Annotations')
        self.metadata.set_description('')
        self.metadata.set_created_by('Dick')
        self.assertEqual(len(self.metadata.to_dict()["annotations"]), 2)

        print ('1.3. Metadata Annotations')
        self.metadata.set_description('xxxxx')
        self.assertEqual(len(self.metadata.to_dict()["annotations"]), 3)
        print('\nTest 1.2 ok')

        print ('1.4. Reload metadata annotations')
        json_metadata = self.metadata.to_json()
        print (json_metadata)
        dict_metadata = json.loads(json_metadata)
        reload_metadata = Metadata(**dict_metadata)
        json_reload_metadata = reload_metadata.to_json()
        print(json_reload_metadata)
        self.assertEqual(json_metadata, json_reload_metadata)


if __name__ == '__main__':
    unittest.main()
