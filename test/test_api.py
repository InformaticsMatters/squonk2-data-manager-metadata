import unittest
import json
from data_manager_metadata.metadata import (Metadata,
                                            LabelAnnotation,
                                            FieldsDescriptorAnnotation,
                                            ServiceExecutionAnnotation)

from data_manager_metadata.annotation_utils import est_schema_field_type
from data_manager_metadata.exceptions import (ANNOTATION_ERRORS,
                                              AnnotationValidationError)

from data_manager_metadata.data_tier_api import post_dataset_metadata

class DataTierTestCase(unittest.TestCase):

    def test_01_post_dataset_metadata(self):
        print ('1.1 post_dataset_metadata')
        self.dataset_metadata = \
            post_dataset_metadata\
                ('test',
                 'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
                 'description','Fred')

        self.assertEqual(self.dataset_metadata['dataset_name'],'test')
        print(self.dataset_metadata)

        print('\nTest 1.1 ok')


if __name__ == '__main__':
    unittest.main()
