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
        output_JSONData = json.dumps(metadata.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)

        # 2. LabelAnnotation
        print ('\n2. Label Annotation')
        annotation1 = LabelAnnotation('label1', 'value1', 'label1name')
        annotation2 = LabelAnnotation('label2', 'value2')
        output_JSONData = json.dumps(annotation1.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)
        output_JSONData = json.dumps(annotation2.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)
        self.assertEqual(annotation1.to_dict(), {'label': 'label1', 'value': 'value1'})
        self.assertEqual(annotation2.to_dict(), {'label': 'label2', 'value': 'value2'})

        # 3. FieldDescriptorAnnotation
        print ('\n3. Field Description Annotation')
        annotation3 = FieldDescriptorAnnotation('Supplier 1', 'A description', 'Dataset1')
        annotation3.add_field('smiles', 'string', 'standardized smiles')
        annotation3.add_field('ID', 'string', 'Molecule Identifier')
        annotation3.add_field('extra', 'string', 'extra field')
        field2 = annotation3.get_field('ID')
        print(field2)
        field3 = annotation3.get_field('extra')
        print(field3)
        annotation3.remove_field('extra')
        output_JSONData = json.dumps(annotation3.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)

        # 4. ServiceExecutionAnnotation
        print ('\n4. Service Execution Annotation')
        params = {'param1': 'p-value1', 'param2': 'p-value2'}
        annotation4 = ServiceExecutionAnnotation('Jupyter notebook', '1.0', 'User 1',
                                                 params, 'Supplier 1', 'A description',
                                                 'Serv1name')
        annotation4.add_field('smiles', 'string', 'standardized smiles')
        annotation4.add_field('ID', 'string', 'Molecule Identifier')
        params_yaml = annotation4.parameters_to_yaml()
        print (params_yaml)
        output_JSONData = json.dumps(annotation4.to_json(), indent=4)
        output_annotation4 = json.loads(output_JSONData)
        print(output_annotation4)

        # 5. Add annotations to Metadata
        print ('\n5. Add annotations to Metadata')
        metadata.add_annotation(annotation1)
        metadata.add_annotation(annotation2)
        metadata.add_annotation(annotation3)
        metadata.add_annotation(annotation4)
        output_JSONData = json.dumps(metadata.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)

        # 6. Get annotations from Metadata
        print ('\n6. Get annotations from Metadata')
        output_obj = metadata.get_annotation('label1name')
        output_JSONData = json.dumps(output_obj.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)
        output_obj = metadata.get_annotation('label2')
        output_JSONData = json.dumps(output_obj.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)

        # 7. Remove annotation from Metadata
        print ('\n7. Remove annotations from Metadata')
        metadata.remove_annotation('label1name')
        output_JSONData = json.dumps(metadata.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)

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


if __name__ == '__main__':
    unittest.main()
