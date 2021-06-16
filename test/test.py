import unittest
import json
import jsonpickle
from data_manager_metadata.metadata import (Metadata,
                                            LabelAnnotation,
                                            FieldDescriptorAnnotation,
                                            ServiceExecutionAnnotation)

class MyTestCase(unittest.TestCase):

    def test_metadata(self):
        # 1. Metadata
        print ('1. Metadata')
        annotations_list = []
        metadata = Metadata('test','test description','bob',annotations_list)
        results_metadata = {'dataset_name': 'test', 'description': 'test description',
                            'created_by': 'bob', 'annotations': []}
        self.assertEqual(metadata.to_dict(), results_metadata)
        self.assertEqual(metadata.get_dataset_name(), results_metadata['dataset_name'])
        self.assertEqual(metadata.get_description(), results_metadata['description'])
        self.assertEqual(metadata.get_created_by(), results_metadata['created_by'])
        self.assertEqual(metadata.get_metadata_version(), '0.0.1')
        print('\nok')

        # 2. LabelAnnotation
        print ('\n2. Label Annotation')
        annotation1 = LabelAnnotation('label1', 'value1', 'label1name')
        results1 = {'annotation': {'name': 'label1name', 'type': 'label'},
                    'label': 'label1', 'value': 'value1'}
        annotation2 = LabelAnnotation('label2', 'value2')
        results2 = {'annotation': {'name': 'label2', 'type': 'label'},
                    'label': 'label2', 'value': 'value2'}
        self.assertEqual(annotation1.to_dict(), results1)
        self.assertEqual(annotation2.to_dict(), results2)
        print('\nok')

        # 3. FieldDescriptorAnnotation
        print ('\n3. Field Description Annotation')
        fields = {'smiles': {'type': 'string', 'description': 'standardized smiles'},
                  'ID': {'type': 'string', 'description': 'Molecule Identifier'}}
        annotation3 = FieldDescriptorAnnotation('Supplier 1', 'A description', fields, 'Dataset1')
        results3 = {'annotation': {'type': 'field_descriptor', 'name': 'Dataset1'},
                    'origin': 'Supplier 1', 'description': 'A description',
                    'fields': {'smiles': {'type': 'string',
                                          'description': 'standardized smiles'},
                               'ID': {'type': 'string', 'description': 'Molecule Identifier'}}}
        output_JSONData = json.dumps(annotation3.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)
        self.assertEqual(annotation3.to_dict(), results3)
        print('\nok')

        # 4. ServiceExecutionAnnotation
        print ('\n4. Service Execution Annotation')
        params = {'param1': 'p-value1', 'param2': 'p-value2'}
        annotation4 = ServiceExecutionAnnotation('Jupyter notebook', '1.0', 'User 1',
                                                 params, 'Supplier 1', 'A description', fields,
                                                 'Serv1name')
        results4 = {'field_descriptor':
                        {'annotation': {'type': 'service_execution', 'name': 'Serv1name'},
                                         'origin': 'Supplier 1', 'description': 'A description',
                                         'fields': {'smiles': {'type': 'string',
                                                               'description': 'standardized smiles'}
                                             , 'ID': {'type': 'string',
                                                      'description': 'Molecule Identifier'}}},
                    'service': 'Jupyter notebook', 'service_version': '1.0',
                    'service_user': 'User 1',
                    'parameters': {'param1': 'p-value1', 'param2': 'p-value2'}}
        params_yaml = annotation4.parameters_to_yaml()
        print (params_yaml)
        output_JSONData = json.dumps(annotation4.to_json(), indent=4)
        output_annotation4 = json.loads(output_JSONData)
        print(output_annotation4)
        self.assertEqual(annotation4.to_dict(), results4)
        print('\nok')

        # 5. Add annotations to Metadata
        print ('\n5. Add annotations to Metadata')
        metadata.add_annotation(annotation1)
        metadata.add_annotation(annotation2)
        metadata.add_annotation(annotation3)
        metadata.add_annotation(annotation4)
        self.assertEqual(len(metadata.to_dict()['annotations']), 4)
        print('\nok')

        # 6. Get annotations from Metadata
        print ('\n6. Get annotations from Metadata')
        output_obj1 = metadata.get_annotation('label1name')
        output_obj2 = metadata.get_annotation('label2')
        self.assertEqual(output_obj1.to_dict(), results1)
        self.assertEqual(output_obj2.to_dict(), results2)
        print('\nok')

        # 7. Remove annotation from Metadata
        print ('\n7. Remove annotations from Metadata')
        metadata.remove_annotation('label1name')
        output_JSONData = json.dumps(metadata.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)
        self.assertEqual(len(metadata.to_dict()['annotations']), 3)
        print('\nok')

        # 8. Simulate restoring metadata (via json) by pickling
        print ('\n8. Pickle and Unpickle metatdata')
        metapickled = metadata.to_pickle()
        print(metapickled)
        metaunpickled = jsonpickle.decode(metapickled)
        upickled_output_JSONData = json.dumps(metaunpickled.to_json(), indent=4)
        upickled_output_json = json.loads(upickled_output_JSONData)
        print(upickled_output_json)

        self.assertEqual(output_json, upickled_output_json)
        print ('Metadata Output Equal')
        print('\nok')

        # 9. Simulate restoring an annotation (via json) by pickling
        print ('\n9. Pickle and Unpickle annotation')
        annopickled = annotation4.to_pickle()
        print(annopickled)
        announpickled = jsonpickle.decode(annopickled)
        upickled_output_JSONData = json.dumps(announpickled.to_json(), indent=4)
        upickled_output_json = json.loads(upickled_output_JSONData)
        print(upickled_output_json)

        self.assertEqual(output_annotation4, upickled_output_json)
        print ('Annotation Output Equal')
        print('\nok')


if __name__ == '__main__':
    unittest.main()
