import unittest
import json

from data_manager_metadata.metadata import (FieldsDescriptorAnnotation,
                                            ServiceExecutionAnnotation,
                                            _DEFAULT_SYNC_TIME)

from data_manager_metadata.data_tier_api import (
    post_dataset_metadata,
    post_version_metadata,
    patch_dataset_metadata,
    get_version_schema,
    patch_version_metadata,
    get_travelling_metadata,
    patch_travelling_metadata,
    post_travelling_metadata_to_new_dataset,
    post_travelling_metadata_to_existing_dataset
    )

class DataTierTestCase(unittest.TestCase):


    def test_01_post_dataset_metadata(self):
        print ('1.1 post_dataset_metadata')
        input_fields = {
            'smiles': {'type': 'string', 'description': 'standardized smiles',
                       'required': True, 'active': True},
            'uuid': {'type': 'string', 'description': 'Molecule Identifier',
                     'required': True, 'active': True},
            'id': {'type': 'string', 'description': 'File Identifier',
                   'required': False, 'active': True},
            }
        annotation1 = FieldsDescriptorAnnotation('Supplier 1', 'A description',
                                                 input_fields)


        dataset_metadata, dataset_schema = \
            post_dataset_metadata\
                ('test dataset',
                 'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
                 'description',
                 'Fred',
                 annotations=annotation1.to_dict())

        self.assertEqual(dataset_metadata['dataset_name'],'test dataset')
        self.assertEqual(dataset_schema['description'],'description')
        print(dataset_metadata)

        print('\nTest 1.1 ok')


    def test_02_post_version_metadata(self):
        print ('2.1 post_version_metadata')

        dataset_metadata, dummy = \
            post_dataset_metadata\
                ('test dataset',
                 'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
                 'description of the dataset','Fred',)

        version_metadata, version_schema = \
            post_version_metadata\
                (dataset_metadata, 1)

        self.assertEqual(version_metadata['dataset_name'],'test dataset')
        self.assertEqual(version_metadata['dataset_version'],1)
        print(version_metadata)
        print(version_schema)

        print('\nTest 2.1 ok')


    def test_03_patch_dataset_metadata(self):
        print ('3.1 patch_dataset_metadata')

        dataset_metadata, dummy = \
            post_dataset_metadata\
                ('test dataset',
                 'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
                 'first description',
                 'Fred')

        self.assertEqual(dataset_metadata['description'],'first description')

        labels_list = [{'type': 'LabelAnnotation',
                        'label': 'label1',
                        'value': 'value1',
                        'active': True}]

        new_dataset_metadata, new_dataset_schema = \
            patch_dataset_metadata(dataset_metadata,
                                   description='new description',
                                   labels=labels_list)

        self.assertEqual(new_dataset_metadata['description'],'new description')
        self.assertEqual(len(new_dataset_metadata['labels']),1)
        self.assertEqual(len(new_dataset_schema['labels']),1)
        print(new_dataset_metadata)

        print('\nTest 3.1 ok')


    def test_04_get_version_schema(self):
        print ('4.1 get_version_schema')

        dataset_metadata, dummy = \
            post_dataset_metadata\
                ('test dataset',
                 'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
                 'description of the dataset','Fred',)

        version_metadata, version_schema = \
            post_version_metadata\
                (dataset_metadata, 1)

        labels_list = [{'type': 'LabelAnnotation',
                        'label': 'label1',
                        'value': 'value1',
                        'active': True}]

        new_dataset_metadata, dummy = \
            patch_dataset_metadata(dataset_metadata,
                                   description='new description',
                                   labels=labels_list)

        new_version_schema = get_version_schema(new_dataset_metadata,
                                                version_metadata)

        self.assertEqual(len(version_schema['labels']),0)
        print(version_schema)
        self.assertEqual(len(new_version_schema['labels']),1)
        print(new_version_schema)

        print('\nTest 4.1 ok')


    def test_05_patch_version_metadata(self):
        print ('5.1 patch_version_metadata')

        dataset_metadata, dummy = \
            post_dataset_metadata\
                ('test dataset',
                 'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
                 'first description',
                 'Fred')

        version_metadata, version_schema = \
            post_version_metadata\
                (dataset_metadata, 1)

        params = {'param1': 'p-value1', 'param2': 'p-value2'}
        input_fields = {'smiles': {'type': 'string', 'description': 'standardized smiles',
                                       'required': True, 'active': True},
                  'ID': {'type': 'string', 'description': 'Changed File Identifier',
                         'required': False, 'active': True}}
        annotation = ServiceExecutionAnnotation\
            ('Jupyter notebook', '1.0', 'User-1', 'service description',
             'www.example.com/service.html', params, 'Supplier 1', 'A description',
             input_fields)

        annotations_list = annotation.to_dict()

        new_version_metadata, new_version_schema = \
            patch_version_metadata(dataset_metadata,
                                   version_metadata,
                                   annotations=annotations_list)

        self.assertEqual(len(version_metadata['annotations']),0)
        self.assertEqual(len(new_version_metadata['annotations']),1)
        self.assertEqual(len(version_schema['fields']),0)
        self.assertEqual(len(new_version_schema['fields']),2)
        self.assertEqual(len(new_version_schema['required']),1)
        print(new_version_schema)
        print(new_version_metadata)

        print('\nTest 5.1 ok')


    def test_06_get_travelling_metadata(self):
        print ('6.1 get_travelling_metadata')

        labels_list = [{'type': 'LabelAnnotation',
                        'label': 'label1',
                        'value': 'value1',
                        'active': True}]

        dataset_metadata, dummy = \
            post_dataset_metadata\
                ('test dataset',
                 'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
                 'first description',
                 'Fred',
                 labels=labels_list)

        self.assertEqual(dataset_metadata['synchronised_datetime'],
                         _DEFAULT_SYNC_TIME)

        params = {'param1': 'p-value1', 'param2': 'p-value2'}
        input_fields = {'smiles': {'type': 'string', 'description': 'standardized smiles',
                                       'required': True, 'active': True},
                  'ID': {'type': 'string', 'description': 'Changed File Identifier',
                         'required': False, 'active': True}}
        annotation = ServiceExecutionAnnotation\
            ('Jupyter notebook', '1.0', 'User-1', 'service description',
             'www.example.com/service.html', params, 'Supplier 1', 'A description',
             input_fields)

        annotations_list = annotation.to_dict()

        version_metadata, version_schema = \
            post_version_metadata\
                (dataset_metadata, 1,
                 annotations=annotations_list)

        print(dataset_metadata)

        travelling_metadata, travelling_schema = \
            get_travelling_metadata(dataset_metadata,
                                   version_metadata)

        self.assertEqual(len(travelling_metadata['annotations']),1)
        self.assertEqual(len(travelling_metadata['labels']),1)
        self.assertEqual(travelling_metadata['dataset_version'],1)
        self.assertNotEqual(travelling_metadata['synchronised_datetime'],
                            _DEFAULT_SYNC_TIME)
        self.assertEqual(len(travelling_schema['labels']),1)
        self.assertEqual(len(travelling_schema['fields']),2)
        self.assertEqual(len(travelling_schema['required']),1)
        print(travelling_schema)
        print(travelling_metadata)

        print('\nTest 6.1 ok')


    def test_07_post_travelling_metadata_to_new_dataset(self):
        print ('7.1 post_travelling_metadata_to_new_dataset')

        labels_list = [{'type': 'LabelAnnotation',
                        'label': 'label1',
                        'value': 'value1',
                        'active': True}]

        dataset_metadata, dummy = \
            post_dataset_metadata\
                ('test dataset',
                 'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
                 'first description',
                 'Fred',
                 labels=labels_list)

        params = {'param1': 'p-value1', 'param2': 'p-value2'}
        input_fields = {'smiles': {'type': 'string', 'description': 'standardized smiles',
                                       'required': True, 'active': True},
                  'ID': {'type': 'string', 'description': 'Changed File Identifier',
                         'required': False, 'active': True}}
        annotation = ServiceExecutionAnnotation\
            ('Jupyter notebook', '1.0', 'User-1', 'service description',
             'www.example.com/service.html', params, 'Supplier 1', 'A description',
             input_fields)

        annotations_list = annotation.to_dict()

        version_metadata, version_schema = \
            post_version_metadata\
                (dataset_metadata, 1,
                 annotations=annotations_list)

        travelling_metadata, travelling_schema = \
            get_travelling_metadata(dataset_metadata,
                                   version_metadata)

        new_dataset, new_dataset_schema, new_version, new_schema = \
            post_travelling_metadata_to_new_dataset (travelling_metadata, 2)

        print(new_dataset)
        print(new_dataset_schema)
        print(new_version)
        print(new_schema)

        self.assertEqual(len(new_dataset['annotations']),0)
        self.assertEqual(len(new_dataset['labels']),1)
        self.assertEqual(new_dataset['synchronised_datetime'],
                         _DEFAULT_SYNC_TIME)
        self.assertEqual(len(new_dataset_schema['labels']),1)
        self.assertEqual(len(new_version['annotations']),1)
        self.assertEqual(len(new_version['labels']),0)
        self.assertEqual(new_version['dataset_version'],2)
        self.assertEqual(new_version['synchronised_datetime'],
                         _DEFAULT_SYNC_TIME)
        self.assertEqual(len(new_schema['labels']),1)
        self.assertEqual(len(new_schema['fields']),2)
        self.assertEqual(len(new_schema['required']),1)

        print('\nTest 7.1 ok')


    def test_08_patch_travelling_metadata_to_existing_dataset(self):
        print('8.1 patch_travelling_metadata_to_existing_dataset')

        labels_list = [{'type': 'LabelAnnotation',
                        'label': 'label1',
                        'value': 'value1',
                        'active': True}]

        dataset_metadata, dummy = \
            post_dataset_metadata \
                ('test dataset',
                 'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
                 'first description',
                 'Fred',
                 labels=labels_list)

        params = {'param1': 'p-value1', 'param2': 'p-value2'}
        input_fields = {
            'smiles': {'type': 'string', 'description': 'standardized smiles',
                       'required': True, 'active': True},
            'ID': {'type': 'string', 'description': 'Changed File Identifier',
                   'required': False, 'active': True}}
        annotation = ServiceExecutionAnnotation \
            ('Jupyter notebook', '1.0', 'User-1', 'service description',
             'www.example.com/service.html', params, 'Supplier 1', 'A description',
             input_fields)

        annotations_list = annotation.to_dict()

        version_metadata, version_schema = \
            post_version_metadata \
                (dataset_metadata, 1,
                 annotations=annotations_list)

        travelling_metadata, travelling_schema = \
            get_travelling_metadata(dataset_metadata,
                                    version_metadata)

        self.assertEqual(len(travelling_metadata['labels']), 1)

        # Push dictionary to file to test the download/upload
        with open('testfile.meta', "w") as meta_file:
            json.dump(travelling_metadata, meta_file)

        labels2_list = [{'type': 'LabelAnnotation',
                         'label': 'label2',
                         'value': 'value2',
                         'active': True}]

        # Patch a label to the travelling metadata
        with open('testfile.meta', "r") as meta_file:
            new_travelling_metadata, new_travelling_schema = \
                patch_travelling_metadata(json.load(meta_file),
                                          labels=labels2_list)
            self.assertEqual(len(new_travelling_metadata['labels']), 2)

        # Patch a label to the original metadata
        labels3_list = [{'type': 'LabelAnnotation',
                         'label': 'label3',
                         'value': 'value3',
                         'active': True}]

        new_dataset_metadata, new_dataset_version = \
            patch_dataset_metadata(dataset_metadata,
                                   labels=labels3_list)
        self.assertEqual(len(new_dataset_metadata['labels']), 2)

        existing_dataset, existing_schema, new_version, new_schema = \
            post_travelling_metadata_to_existing_dataset\
                (new_travelling_metadata,new_dataset_metadata, 2)

        print(existing_dataset)
        print(existing_schema)
        print(new_version)
        print(new_schema)

        self.assertEqual(len(existing_dataset['annotations']), 0)
        self.assertEqual(len(existing_dataset['labels']), 3)
        self.assertEqual(existing_dataset['synchronised_datetime'],
                         _DEFAULT_SYNC_TIME)
        self.assertEqual(len(existing_schema['labels']), 3)
        self.assertEqual(len(new_version['annotations']), 1)
        self.assertEqual(len(new_version['labels']), 0)
        self.assertEqual(new_version['dataset_version'], 2)
        self.assertEqual(new_version['synchronised_datetime'],
                         _DEFAULT_SYNC_TIME)
        self.assertEqual(len(new_schema['labels']), 3)
        self.assertEqual(len(new_schema['fields']), 2)
        self.assertEqual(len(new_schema['required']), 1)

        print('\nTest 8.1 ok')


if __name__ == '__main__':
    unittest.main()
