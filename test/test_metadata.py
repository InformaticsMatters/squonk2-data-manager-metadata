import unittest
import json
from data_manager_metadata.metadata import (
    Metadata,
    LabelAnnotation,
    FieldsDescriptorAnnotation,
    ServiceExecutionAnnotation,
)

from data_manager_metadata.annotation_utils import est_schema_field_type
from data_manager_metadata.exceptions import (
    ANNOTATION_ERRORS,
    AnnotationValidationError,
)


class MetadataTestCase(unittest.TestCase):

    maxDiff = None
    metadata = Metadata('test', '0000-1111', '', 'Bob')

    def test_01_metadata(self):
        print('1.1 Metadata')
        results_metadata = {
            'dataset_name': 'test',
            'dataset_uuid': '0000-1111',
            'description': '',
            'created_by': 'Bob',
            'annotations': [],
            'labels': [],
        }
        self.assertEqual(
            self.metadata.get_dataset_name(), results_metadata['dataset_name']
        )
        self.assertEqual(
            self.metadata.get_dataset_uuid(), results_metadata['dataset_uuid']
        )
        self.assertEqual(
            self.metadata.get_description(), results_metadata['description']
        )
        self.assertEqual(self.metadata.get_created_by(), results_metadata['created_by'])
        self.assertEqual(self.metadata.get_metadata_version(), '0.0.1')
        print('\nTest 1.1 ok')

        print('1.2. Metadata Annotations')
        self.metadata.set_description('test description')
        self.metadata.set_created_by('Dick')
        self.assertEqual(len(self.metadata.to_dict()["annotations"]), 2)
        print('\nTest 1.2 ok')

        print('1.3. Reload metadata annotations')
        json_metadata = self.metadata.to_json()
        dict_metadata = json.loads(json_metadata)
        reload_metadata = Metadata(**dict_metadata)
        json_reload_metadata = reload_metadata.to_json()
        self.assertEqual(json_metadata, json_reload_metadata)
        print('\nTest 1.3 ok')

    def test_02_label_annotations(self):
        print('\n2.1. Label Annotation')
        annotation1 = LabelAnnotation('label1', 'value1')
        results1 = {'type': 'LabelAnnotation', 'label': 'label1', 'value': 'value1'}
        self.assertEqual(annotation1.__class__.__name__, results1['type'])
        self.assertEqual(annotation1.get_label(), results1['label'])
        print('\nTest 2.1 ok')

        print('\n2.2. Label Annotation to Metadata')
        self.metadata.add_label(annotation1)
        self.assertEqual(len(self.metadata.to_dict()["labels"]), 1)
        self.assertEqual(len(self.metadata.to_dict()["annotations"]), 2)
        print(self.metadata.to_json())
        print('\nTest 2.2 ok')

        print('\n2.3. Validation Errors')
        try:
            LabelAnnotation('label1toolonganame', 'value1')
        except AnnotationValidationError as e:
            self.assertEqual(e.annotation_type, 'LabelAnnotation')
            self.assertEqual(
                e.message, ANNOTATION_ERRORS['LabelAnnotation']['1']['message']
            )
        else:
            self.fail("This should normally fail")

        print('\nTest 2.3 ok')

        print('2.3. Reload metadata annotations')
        json_metadata = self.metadata.to_json()
        dict_metadata = json.loads(json_metadata)
        reload_metadata = Metadata(**dict_metadata)
        json_reload_metadata = reload_metadata.to_json()
        self.assertEqual(json_metadata, json_reload_metadata)
        print('\nTest 2.3 ok')

        print('\n2.4. Address Label Annotation with reference')
        annotation1 = LabelAnnotation('@label1', 'value1', reference='pose')
        results1 = {
            'type': 'LabelAnnotation',
            'label': '@label1',
            'value': 'value1',
            'reference': "pose",
        }
        self.assertEqual(annotation1.__class__.__name__, results1['type'])
        self.assertEqual(annotation1.get_label(), results1['label'])
        self.assertEqual(annotation1.get_reference(), results1['reference'])
        print('\nTest 2.4 ok')

        print('\n2.5. Hash Label Annotation')
        annotation1 = LabelAnnotation('#label1', 'hashvalue1')
        results1 = {
            'type': 'LabelAnnotation',
            'label': '#label1',
            'value': 'value1',
        }
        self.assertEqual(annotation1.__class__.__name__, results1['type'])
        self.assertEqual(annotation1.get_label(), results1['label'])
        print('\nTest 2.5 ok')

    def test_03_fields_annotations(self):
        print('\n3.1. FieldsDescriptor Annotation')
        input_fields = {
            'smiles': {
                'type': 'string',
                'description': 'standardized smiles',
                'required': True,
                'active': True,
            },
            'uuid': {
                'type': 'string',
                'description': 'Molecule Identifier',
                'required': True,
                'active': True,
            },
            'id': {
                'type': 'string',
                'description': 'File Identifier',
                'required': False,
                'active': True,
            },
            'dynamic': {
                'type': 'string',
                'description': 'A dynamically named field',
                'expression': '{{ dynamicFieldName }}',
                'required': False,
                'active': True,
            },
        }
        spec = {'variables': {'dynamicFieldName': 'my_name'}}
        expected_fields = {
            'smiles': {
                'type': 'string',
                'description': 'standardized smiles',
                'required': True,
                'active': True,
            },
            'uuid': {
                'type': 'string',
                'description': 'Molecule Identifier',
                'required': True,
                'active': True,
            },
            'id': {
                'type': 'string',
                'description': 'File Identifier',
                'required': False,
                'active': True,
            },
            'my_name': {
                'type': 'string',
                'description': 'A dynamically named field',
                'required': False,
                'active': True,
            },
        }
        annotation3 = FieldsDescriptorAnnotation(
            'Supplier 1', 'A description', input_fields, spec
        )
        output_fields = annotation3.get_fields()
        self.assertEqual(output_fields, expected_fields)
        self.assertEqual(annotation3.get_property('smiles'), input_fields['smiles'])
        self.assertEqual(annotation3.get_property('uuid'), input_fields['uuid'])

        # change field type
        annotation3.add_field(field_name='id', prop_type='number')
        self.assertNotEqual(annotation3.get_property('id'), input_fields['id'])

        # set to inactive
        annotation3.add_field(field_name='id', active=False)
        self.assertNotEqual(annotation3.get_property('id'), input_fields['id'])
        self.assertEqual(len(annotation3.get_fields(False)), 3)

        output_JSONData = json.dumps(annotation3.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)
        print('\nTest 3.1 ok')

        print('\n3.2. Fields Annotation to Metadata')
        self.metadata.add_annotation(annotation3)
        self.assertEqual(len(self.metadata.to_dict()["annotations"]), 3)
        print('\nTest 3.2 ok')

        print('\n3.3. Transfer Fields Annotation to new Fields Annotation')
        annotation3_3 = FieldsDescriptorAnnotation('Supplier 1', 'A description', "")
        # Transfer active only
        annotation3_3.add_fields(annotation3.get_fields())
        self.assertEqual(annotation3.get_fields(), annotation3_3.get_fields())
        # Transfer active and inactive
        annotation3_3.add_fields(annotation3.get_fields(True))
        self.assertEqual(annotation3.get_fields(True), annotation3_3.get_fields(True))
        print('\nTest 3.3 ok')

        print('\n3.4. Validation Errors')
        invalid_field = "x" * 256

        try:
            FieldsDescriptorAnnotation(invalid_field, 'A description', input_fields)
        except AnnotationValidationError as e:
            self.assertEqual(e.annotation_type, 'FieldsDescriptorAnnotation')
            self.assertEqual(
                e.message,
                ANNOTATION_ERRORS['FieldsDescriptorAnnotation']['1']['message'],
            )
        else:
            self.fail("This should normally fail")

        try:
            FieldsDescriptorAnnotation('supplier 1', invalid_field, input_fields)
        except AnnotationValidationError as e:
            self.assertEqual(e.annotation_type, 'FieldsDescriptorAnnotation')
            self.assertEqual(
                e.message,
                ANNOTATION_ERRORS['FieldsDescriptorAnnotation']['2']['message'],
            )
        else:
            self.fail("This should normally fail")

        try:
            input_fieldx = {
                'smilesveryxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx': {
                    'type': 'string',
                    'description': 'standardized smiles',
                    'required': True,
                    'active': True,
                }
            }
            FieldsDescriptorAnnotation('Supplier x', 'A description', input_fieldx)
        except AnnotationValidationError as e:
            self.assertEqual(e.annotation_type, 'FieldsDescriptorAnnotation')
            self.assertEqual(
                e.message,
                'Field name: smilesveryxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx, length must be from 1 to 50 characters',
            )
        else:
            self.fail("This should normally fail")

        try:
            input_fieldy = {
                'smiles': {
                    'type': 'blob',
                    'description': 'standardized smiles',
                    'required': True,
                    'active': True,
                }
            }
            FieldsDescriptorAnnotation('Supplier x', 'A description', input_fieldy)
        except AnnotationValidationError as e:
            self.assertEqual(e.annotation_type, 'FieldsDescriptorAnnotation')
            self.assertEqual(e.error, '4')
        else:
            self.fail("This should normally fail")

        print('\nTest 3.4 ok')

        print('3.5. Reload metadata annotations')
        json_metadata = self.metadata.to_json()
        dict_metadata = json.loads(json_metadata)
        reload_metadata = Metadata(**dict_metadata)
        json_reload_metadata = reload_metadata.to_json()
        self.assertEqual(json_metadata, json_reload_metadata)
        print('\nTest 3.5 ok')

    def test_04_service_execution(self):
        print('\n4. Service Execution Annotation')
        params = {'param1': 'p-value1', 'param2': 'p-value2'}
        input_fields = {
            'smiles': {
                'type': 'string',
                'description': 'standardized smiles',
                'required': True,
                'active': True,
            },
            'ID': {
                'type': 'string',
                'description': 'Changed File Identifier',
                'required': False,
                'active': True,
            },
        }
        annotation4 = ServiceExecutionAnnotation(
            'Jupyter notebook',
            '1.0',
            'User-1',
            'service description',
            'www.example.com/service.html',
            params,
            'Supplier 1',
            'A description',
            input_fields,
        )
        self.assertEqual(annotation4.get_service(), 'Jupyter notebook')
        self.assertEqual(annotation4.get_service_parameters(), params)
        output_JSONData = json.dumps(annotation4.to_json(), indent=4)
        output_json = json.loads(output_JSONData)
        print(output_json)
        print('\nTest 4.1 ok')

        print('\n4.2. Service Execution Annotation to Metadata')
        self.metadata.add_annotation(annotation4)
        self.assertEqual(len(self.metadata.to_dict()["annotations"]), 4)
        print('\nTest 4.2 ok')

        print('\n4.3. Validation Errors')
        invalid_field = "x" * 256

        try:
            ServiceExecutionAnnotation(
                '',
                '1.0',
                'User 1',
                'service description',
                'www.example.com/service.html',
                params,
                'Supplier 1',
                'A description',
                input_fields,
            )
        except AnnotationValidationError as e:
            self.assertEqual(e.annotation_type, 'ServiceExecutionAnnotation')
            self.assertEqual(
                e.message,
                ANNOTATION_ERRORS['ServiceExecutionAnnotation']['1']['message'],
            )
        else:
            self.fail("This should normally fail")

        try:
            ServiceExecutionAnnotation(
                'Jupyter notebook',
                invalid_field,
                'User 1',
                'service description',
                'www.example.com/service.html',
                params,
                'Supplier 1',
                'A description',
                input_fields,
            )
        except AnnotationValidationError as e:
            self.assertEqual(e.annotation_type, 'ServiceExecutionAnnotation')
            self.assertEqual(
                e.message,
                ANNOTATION_ERRORS['ServiceExecutionAnnotation']['2']['message'],
            )
        else:
            self.fail("This should normally fail")

        try:
            ServiceExecutionAnnotation(
                'Jupyter notebook',
                '1.0',
                invalid_field,
                'service description',
                'www.example.com/service.html',
                params,
                'Supplier 1',
                'A description',
                input_fields,
            )
        except AnnotationValidationError as e:
            self.assertEqual(e.annotation_type, 'ServiceExecutionAnnotation')
            self.assertEqual(
                e.message,
                ANNOTATION_ERRORS['ServiceExecutionAnnotation']['3']['message'],
            )
        else:
            self.fail("This should normally fail")

        try:
            ServiceExecutionAnnotation(
                'Jupyter notebook',
                '1.0',
                'User 1',
                invalid_field,
                'www.example.com/service.html',
                params,
                'Supplier 1',
                'A description',
                input_fields,
            )
        except AnnotationValidationError as e:
            self.assertEqual(e.annotation_type, 'ServiceExecutionAnnotation')
            self.assertEqual(
                e.message,
                ANNOTATION_ERRORS['ServiceExecutionAnnotation']['4']['message'],
            )
        else:
            self.fail("This should normally fail")

        try:
            ServiceExecutionAnnotation(
                'Jupyter notebook',
                '1.0',
                'User 1',
                'service description',
                invalid_field,
                params,
                'Supplier 1',
                'A description',
                input_fields,
            )
        except AnnotationValidationError as e:
            self.assertEqual(e.annotation_type, 'ServiceExecutionAnnotation')
            self.assertEqual(
                e.message,
                ANNOTATION_ERRORS['ServiceExecutionAnnotation']['5']['message'],
            )
        else:
            self.fail("This should normally fail")

        print('\nTest 4.3 ok')

        print('4.4. Reload metadata annotations')
        json_metadata = self.metadata.to_json()
        dict_metadata = json.loads(json_metadata)
        reload_metadata = Metadata(**dict_metadata)
        json_reload_metadata = reload_metadata.to_json()
        self.assertEqual(json_metadata, json_reload_metadata)
        print('\nTest 4.4 ok')

    def test_05_load_annotations_in_new_metadata(self):
        print('\n5. Get annotations from Metadata and add to new Metadata')
        annotations_old = self.metadata.get_annotations_json()
        print(annotations_old)
        metadata_new = Metadata(
            'New dataset',
            '0000-2222',
            'Created from the first dataset by a workflow',
            'Harry',
        )
        metadata_new.add_annotations(self.metadata.get_annotations_dict())
        annotations_new = metadata_new.get_annotations_json()
        print(annotations_new)
        self.assertEqual(annotations_old, annotations_new)
        print('\nTest 5 ok')

    def test_07_label_list(self):
        print('\n7. Test label list from LabelAnnotations')
        labels = self.metadata.get_labels()
        self.assertEqual(len(labels), 1)

        print('add label2')
        label = LabelAnnotation('label2', 'value2')
        self.metadata.add_label(label)
        labels = self.metadata.get_labels()
        self.assertEqual(len(labels), 2)

        print('add label3 with empty value')
        label3 = LabelAnnotation('label3')
        self.metadata.add_label(label3)
        labels = self.metadata.get_labels(labels_only=True)
        self.assertEqual(len(labels), 3)

        print('Change label2 value')
        label = LabelAnnotation('label2', 'value changed')
        self.metadata.add_label(label)
        labels = self.metadata.get_labels()
        print(labels)
        self.assertEqual(len(labels), 3)

        print('Make label3 inactive')
        label = LabelAnnotation('label3', active=False)
        self.metadata.add_label(label)
        labels = self.metadata.get_labels()
        self.assertEqual(len(labels), 3)
        labels = self.metadata.get_labels(active=True)
        self.assertEqual(len(labels), 2)

        print('Make label2 inactive')
        label = LabelAnnotation('label2', active=False)
        self.metadata.add_label(label)
        labels = self.metadata.get_labels()
        self.assertEqual(len(labels), 3)
        labels = self.metadata.get_labels(active=True)
        self.assertEqual(len(labels), 1)

        print('Make label3 active again')
        label = LabelAnnotation('label3', active=True)
        self.metadata.add_label(label)
        labels = self.metadata.get_labels()
        self.assertEqual(len(labels), 3)
        labels = self.metadata.get_labels(active=True)
        self.assertEqual(len(labels), 2)

        print('Make label3 inactive again')
        label = LabelAnnotation('label3', active=False)
        self.metadata.add_label(label)
        labels = self.metadata.get_labels()
        self.assertEqual(len(labels), 3)
        labels = self.metadata.get_labels(active=True)
        self.assertEqual(len(labels), 1)

        print('Make label2 active again')
        label = LabelAnnotation('label2', 'value changed', active=True)
        self.metadata.add_label(label)
        labels = self.metadata.get_labels()
        self.assertEqual(len(labels), 3)
        labels = self.metadata.get_labels(active=True)
        self.assertEqual(len(labels), 2)

        print('self.metadata.get_labels(active=True)')
        labels = self.metadata.get_labels(active=True)
        self.assertEqual(len(labels), 2)

        print('self.metadata.get_labels(active=True,labels_only=True)')
        labels = self.metadata.get_labels(True, True)
        self.assertEqual(len(labels), 2)
        self.assertEqual(labels, {'label2': 'value changed', 'label1': 'value1'})

        print('Number of labels is correct')
        print('\nTest 7 ok')

        print('7.1. Reload metadata annotations')
        json_metadata = self.metadata.to_json()
        dict_metadata = json.loads(json_metadata)
        reload_metadata = Metadata(**dict_metadata)
        json_reload_metadata = reload_metadata.to_json()
        self.assertEqual(json_metadata, json_reload_metadata)
        labels = reload_metadata.get_labels(True, True)
        self.assertEqual(len(labels), 2)
        self.assertEqual(labels, {'label2': 'value changed', 'label1': 'value1'})
        print('\nTest 7.1 ok')

    def test_08_json_schema(self):
        print('\n8. Test json schema extract from Metadata')
        expected_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema#',
            '$id': 'https://example.com/product.schema.json',
            'title': 'test',
            'description': 'test description',
            'version': 0,
            'type': 'object',
            'fields': {
                'smiles': {'type': 'string', 'description': 'standardized smiles'},
                'uuid': {'type': 'string', 'description': 'Molecule Identifier'},
                'my_name': {
                    'type': 'string',
                    'description': 'A dynamically named field',
                },
                'ID': {'type': 'string', 'description': 'Changed File Identifier'},
            },
            'required': ['smiles', 'uuid'],
            'labels': {'label2': 'value changed', 'label1': 'value1'},
        }
        schema = self.metadata.get_json_schema()
        self.assertEqual(schema, expected_schema)
        print('Json Schema matches expected schema')

        # Add a FieldsDescriptor and regenerate
        input_fields = {
            'test1': {'type': 'string', 'description': 'test1', 'required': True}
        }
        expected_fields = {
            'smiles': {'type': 'string', 'description': 'standardized smiles'},
            'uuid': {'type': 'string', 'description': 'Molecule Identifier'},
            'my_name': {'type': 'string', 'description': 'A dynamically named field'},
            'ID': {'type': 'string', 'description': 'Changed File Identifier'},
            'test1': {'type': 'string', 'description': 'test1'},
        }
        expected_req = ['smiles', 'uuid', 'test1']
        annotation = FieldsDescriptorAnnotation(
            'Supplier 1', 'New description', input_fields
        )
        self.metadata.add_annotation(annotation)
        schema = self.metadata.get_json_schema()
        self.assertEqual(schema['fields'], expected_fields)
        self.assertEqual(schema['required'], expected_req)
        print('With added FD annotation, Json Schema matches expected schema')

        # Add a Service Execution and regenerate
        input_fields = {
            'test2': {
                'type': 'string',
                'description': 'test2 - service ex',
                'required': False,
            }
        }
        expected_fields = {
            'smiles': {'type': 'string', 'description': 'standardized smiles'},
            'uuid': {'type': 'string', 'description': 'Molecule Identifier'},
            'my_name': {'type': 'string', 'description': 'A dynamically named field'},
            'ID': {'type': 'string', 'description': 'Changed File Identifier'},
            'test1': {'type': 'string', 'description': 'test1'},
            'test2': {'type': 'string', 'description': 'test2 - service ex'},
        }
        expected_req = ['smiles', 'uuid', 'test1']
        annotation = ServiceExecutionAnnotation(
            'Jupyter notebook',
            '1.0',
            'User-1',
            'service description',
            'www.example.com/service.html',
            {},
            'Supplier 1',
            'A description',
            input_fields,
        )
        self.metadata.add_annotation(annotation)
        schema = self.metadata.get_json_schema()
        print(schema)
        self.assertEqual(schema['fields'], expected_fields)
        self.assertEqual(schema['required'], expected_req)
        print('With added SE annotation, Json Schema matches expected schema')

        print('\nTest 8 ok')

        print('8.1. Reload metadata annotations')
        json_metadata = self.metadata.to_json()
        dict_metadata = json.loads(json_metadata)
        reload_metadata = Metadata(**dict_metadata)
        json_reload_metadata = reload_metadata.to_json()
        self.assertEqual(json_metadata, json_reload_metadata)

        schema = reload_metadata.get_json_schema()
        self.assertEqual(schema['fields'], expected_fields)
        self.assertEqual(schema['required'], expected_req)
        print('\nTest 8.1 ok')

    def test_09_compiled_fields(self):
        # This is used in the file formatters.
        print('\n09. Test compiled fields descriptor extract from Metadata')
        expected_annotation = {
            'fields': {
                'smiles': {
                    'type': 'string',
                    'description': 'standardized smiles',
                    'required': True,
                    'active': True,
                },
                'my_name': {
                    'type': 'string',
                    'description': 'A dynamically named field',
                    'required': False,
                    'active': True,
                },
                'ID': {
                    'type': 'string',
                    'description': 'Changed File Identifier',
                    'required': False,
                    'active': True,
                },
                'uuid': {
                    'type': 'string',
                    'description': 'Molecule Identifier',
                    'required': True,
                    'active': True,
                },
                'test1': {
                    'type': 'string',
                    'description': 'test1',
                    'required': True,
                    'active': True,
                },
                'test2': {
                    'type': 'string',
                    'description': 'test2 - service ex',
                    'required': False,
                    'active': True,
                },
            }
        }
        anno = self.metadata.get_compiled_fields()
        print(anno)
        self.assertEqual(anno['fields'], expected_annotation['fields'])
        print('Compiled fields matches expected fields')

        with open('testfile.annotations', "w", encoding='utf8') as anno_file:
            json.dump(anno, anno_file)
        with open('testfile.annotations', "r", encoding='utf8') as anno_file:
            self.metadata.add_annotations(json.load(anno_file))
            schema = self.metadata.get_json_schema()
            print(schema)

        print('\nTest 09 ok')

        print('9.1. Reload metadata annotations')
        json_metadata = self.metadata.to_json()
        dict_metadata = json.loads(json_metadata)
        reload_metadata = Metadata(**dict_metadata)
        json_reload_metadata = reload_metadata.to_json()
        self.assertEqual(json_metadata, json_reload_metadata)

        anno = reload_metadata.get_compiled_fields()
        self.assertEqual(anno['fields'], expected_annotation['fields'])

        print('\nTest 9.1 ok')

    def test_10_simple_labels_in_schema(self):
        print('\n10. Create simple labels from schema')
        labels_list = [
            {
                'type': 'LabelAnnotation',
                'label': 'label1',
                'value': 'value1',
                'active': True,
            }
        ]
        labels = {'label1': 'value1'}
        metadata_new = Metadata(
            'New dataset',
            '0000-2222',
            'Created from the first dataset by a workflow',
            'Harry',
        )
        metadata_new.add_labels(labels_list)
        schema = metadata_new.get_json_schema()
        print(schema)
        self.assertEqual(schema['labels'], labels)

        print('\nTest 10 ok')

    def test_11_context(self):
        print('\n11. Test annotations context and order')
        expected_fields1 = {
            'fields': {
                'molecule': {
                    'type': 'object',
                    'description': '',
                    'required': False,
                    'active': True,
                },
                'uuid': {
                    'type': 'string',
                    'description': '',
                    'required': False,
                    'active': True,
                },
            }
        }

        expected_fields2 = {
            'fields': {
                'smiles': {
                    'type': 'string',
                    'description': '',
                    'required': False,
                    'active': True,
                }
            }
        }

        metadata1 = Metadata('Dataset 1', '0000-1111', '', 'Tom')
        metadata2 = Metadata('Dataset 2', '0000-2222', '', 'Dick')
        with open('test/input/test1.annotations', "r", encoding='utf8') as anno_file:
            print('metadata 1')
            metadata1.add_annotations(json.load(anno_file))
            fields = metadata1.get_compiled_fields()
            print(fields)
            self.assertEqual(fields['fields'], expected_fields1['fields'])
        with open('test/input/test2.annotations', "r", encoding='utf8') as anno_file_2:
            print('metadata 2')
            metadata2.add_annotations(json.load(anno_file_2))
            fields = metadata2.get_compiled_fields()
            print(fields)
            self.assertEqual(fields['fields'], expected_fields2['fields'])

        print('\nTest 11 ok')

    def test_20_annotation_utilities(self):
        print('\n20. Tests for field types')
        self.assertEqual(est_schema_field_type('1'), 'integer')
        self.assertEqual(est_schema_field_type('1.1'), 'number')
        self.assertEqual(est_schema_field_type('True'), 'boolean')
        self.assertEqual(est_schema_field_type('False'), 'boolean')
        self.assertEqual(
            est_schema_field_type('O=C(CSCc1ccc(Cl)s1)N1CCC(O)CC1'), 'string'
        )
        self.assertEqual(est_schema_field_type('1,2,3'), 'array')
        self.assertEqual(est_schema_field_type('ID1234'), 'string')
        print('\nTest 20 ok')

    def test_30_md_manage(self):
        print('\n30. Tests for md_manage.py to be added')


if __name__ == '__main__':
    unittest.main()
