import unittest
import json
import jsonpickle
from data_manager_metadata.metadata import (Metadata,
                                            LabelAnnotation,
                                            FieldsDescriptorAnnotation,
                                            ServiceExecutionAnnotation)

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
        self.metadata.set_description('test description')
        self.metadata.set_created_by('Dick')
        self.assertEqual(len(self.metadata.to_dict()["annotations"]), 2)

        print (self.metadata.to_json())
        print('\nTest 1.2 ok')

    def test_02_label_annotations(self):
        print ('\n2.1. Label Annotation')
        annotation1 = LabelAnnotation('label1', 'value1')
        results1 = {'type': 'LabelAnnotation', 'label': 'label1', 'value': 'value1'}
        self.assertEqual(annotation1.__class__.__name__, results1['type'])
        self.assertEqual(annotation1.get_label(), results1['label'])
        print('\nTest 2.1 ok')

        print ('\n2.2. Label Annotation to Metadata')
        self.metadata.add_annotation(annotation1)
        self.assertEqual(len(self.metadata.to_dict()["annotations"]), 3)
        print (self.metadata.to_json())
        print('\nTest 2.2 ok')


    def test_03_fields_annotations(self):
        print ('\n3.1. FieldsDescriptor Annotation')
        input_properties = {'smiles': {'type': 'string', 'description': 'standardized smiles',
                                       'required': True, 'active': True},
                            'uuid': {'type': 'uuid', 'description': 'Molecule Identifier',
                                   'required': True, 'active': True},
                            'id': {'type': 'string', 'description': 'File Identifier',
                                   'required': False, 'active': True},
                            }
        annotation3 = FieldsDescriptorAnnotation('Supplier 1', 'A description', input_properties)
        ouput_properties = annotation3.get_properties()
        self.assertEqual(ouput_properties, input_properties)
        self.assertEqual(annotation3.get_property('smiles'), input_properties['smiles'])
        self.assertEqual(annotation3.get_property('uuid'), input_properties['uuid'])

        annotation3.add_property('smiles',prop_type='smiles')
        self.assertNotEqual(annotation3.get_property('smiles'), input_properties['smiles'])
        annotation3.add_property('id',active=False)
        self.assertNotEqual(annotation3.get_property('id'), input_properties['id'])
        self.assertEqual(len(annotation3.get_properties(False)), 2)

        output_JSONData = json.dumps(annotation3.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)
        print('\nTest 3.1 ok')

        print ('\n3.2. Fields Annotation to Metadata')
        self.metadata.add_annotation(annotation3)
        self.assertEqual(len(self.metadata.to_dict()["annotations"]), 4)
        print('\nTest 3.2 ok')

        print ('\n3.3. Transfer Fields Annotation to new Fields Annotation')
        annotation3_3 = FieldsDescriptorAnnotation('Supplier 1', 'A description', "")
        # Transfer active only
        annotation3_3.add_properties(annotation3.get_properties())
        self.assertEqual(annotation3.get_properties(), annotation3_3.get_properties())
        # Transfer active and inactive
        annotation3_3.add_properties(annotation3.get_properties(True))
        self.assertEqual(annotation3.get_properties(True), annotation3_3.get_properties(True))

        print('\nTest 3.3 ok')


    def test_04_service_execution(self):
        print ('\n4. Service Execution Annotation')
        params = {'param1': 'p-value1', 'param2': 'p-value2'}
        input_properties = {'smiles': {'type': 'smiles', 'description': 'standardized smiles',
                                       'required': True, 'active': True},
                  'ID': {'type': 'string', 'description': 'Changed File Identifier',
                         'required': False, 'active': True}}
        annotation4 = ServiceExecutionAnnotation\
            ('Jupyter notebook', '1.0', 'User 1', 'service description',
             'www.example.com/service.html', params, 'Supplier 1', 'A description',
             input_properties)
        self.assertEqual(annotation4.get_service(), 'Jupyter notebook')
        self.assertEqual(annotation4.get_service_parameters(), params)
        output_JSONData = json.dumps(annotation4.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)
        print('\nTest 4.1 ok')

        print ('\n4.2. Service Execution Annotation to Metadata')
        self.metadata.add_annotation(annotation4)
        self.assertEqual(len(self.metadata.to_dict()["annotations"]), 5)
        print('\nTest 4.2 ok')


    def test_05_load_annotations_in_new_metadata(self):
        print ('\n5. Get annotations from Metadata and add to new Metadata')
        annotations_old = self.metadata.get_annotations_json()
        metadata_new = Metadata('New dataset', '0000-2222',
                                'Created from the first dataset by a workflow', 'Harry')
        metadata_new.add_annotations(annotations_old)
        annotations_new = metadata_new.get_annotations_json()
        self.assertEqual(annotations_old, annotations_new)
        print('\nTest 5 ok')


    def test_06_pickle_and_unpickle_metadata (self):
        print ('\n6. Pickle and Unpickle metatdata for saving object into dataset')
        metapickled = jsonpickle.encode(self.metadata)
        metaunpickled = jsonpickle.decode(metapickled)
        self.assertEqual(self.metadata.to_json(), metaunpickled.to_json())
        print ('Metadata Output Equal')
        print('\nTest 6 ok')


    def test_07_json_schema (self):
        print ('\n7. Test json schema extract from FieldsDescriptor')
        expected_schema = {'$schema': 'http://json-schema.org/draft/2019-09/schema#',
                           '$id': 'https://example.com/product.schema.json',
                           'title': 'test', 'description': 'test description',
                           'type': 'object',
                           'properties':
                               {'smiles': {'type': 'smiles', 'description': 'standardized smiles'},
                                'uuid': {'type': 'uuid', 'description': 'Molecule Identifier'},
                                'ID': {'type': 'string', 'description': 'Changed File Identifier'}},
                           'required': ['smiles', 'uuid']}
        schema = (self.metadata.get_json_schema())
        self.assertEqual(schema, expected_schema)
        print ('Json Schema matches expected schema')
        print('\nTest 7 ok')


    def test_08_label_list (self):
        print ('\n8. Test label list from LabelAnnotations')
        labels = (self.metadata.get_labels())
        self.assertEqual(len(labels), 1)
        # add a different label
        label = LabelAnnotation('label2', 'value2')
        self.metadata.add_annotation(label)
        labels = (self.metadata.get_labels())
        self.assertEqual(len(labels), 2)
        # Change label2 value
        label = LabelAnnotation('label2', 'value changed')
        self.metadata.add_annotation(label)
        labels = (self.metadata.get_labels())
        self.assertEqual(len(labels), 2)
        # Make label2 inactive
        label = LabelAnnotation('label2', 'value changed', False)
        self.metadata.add_annotation(label)
        labels = (self.metadata.get_labels(True))
        self.assertEqual(len(labels), 1)
        labels = (self.metadata.get_labels(False))
        self.assertEqual(len(labels), 1)
        labels = (self.metadata.get_labels())
        self.assertEqual(len(labels), 2)
        print(labels)

        print ('Number of labels is correct')
        print('\nTest 8 ok')


    def test_20_label_list (self):
        print ('\n20. Tests for md_manage.py to be added')
        pass

if __name__ == '__main__':
    unittest.main()
