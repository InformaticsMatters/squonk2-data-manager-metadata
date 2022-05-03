import unittest
import os
import json

# from yaml import safe_load
# from decoder import decoder

from data_manager_metadata.metadata import (
    FieldsDescriptorAnnotation,
    ServiceExecutionAnnotation,
    _DEFAULT_SYNC_TIME,
)

from data_manager_metadata.data_tier_api import (
    post_dataset_metadata,
    post_version_metadata,
    patch_dataset_metadata,
    get_version_schema,
    patch_version_metadata,
    get_travelling_metadata,
    patch_travelling_metadata,
    post_travelling_metadata_to_new_dataset,
    post_travelling_metadata_to_existing_dataset,
    create_job_annotations,
)


class DataTierTestCase(unittest.TestCase):
    def test_01_post_dataset_metadata(self):
        print('1.1 post_dataset_metadata')
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
        }
        annotation1 = FieldsDescriptorAnnotation(
            'Supplier 1', 'A description', input_fields
        )

        dataset_metadata, dataset_schema = post_dataset_metadata(
            'test dataset',
            'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
            'description',
            'Fred',
            annotations=annotation1.to_dict(),
        )

        self.assertEqual(dataset_metadata['dataset_name'], 'test dataset')
        self.assertEqual(dataset_schema['description'], 'description')
        print(dataset_metadata)

        print('\nTest 1.1 ok')

    def test_02_post_version_metadata(self):
        print('2.1 post_version_metadata')

        dataset_metadata, dummy = post_dataset_metadata(
            'test dataset',
            'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
            'description of the dataset',
            'Fred',
        )

        version_metadata, version_schema = post_version_metadata(dataset_metadata, 1)

        self.assertEqual(version_metadata['dataset_name'], 'test dataset')
        self.assertEqual(version_metadata['dataset_version'], 1)
        print(version_metadata)
        print(version_schema)

        print('\nTest 2.1 ok')

    def test_03_patch_dataset_metadata(self):
        print('3.1 patch_dataset_metadata')

        dataset_metadata, dummy = post_dataset_metadata(
            'test dataset',
            'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
            'first description',
            'Fred',
        )

        self.assertEqual(dataset_metadata['description'], 'first description')

        labels_list = [
            {
                'type': 'LabelAnnotation',
                'label': 'label1',
                'value': 'value1',
                'active': True,
            }
        ]

        new_dataset_metadata, new_dataset_schema = patch_dataset_metadata(
            dataset_metadata, description='new description', labels=labels_list
        )

        self.assertEqual(new_dataset_metadata['description'], 'new description')
        self.assertEqual(len(new_dataset_metadata['labels']), 1)
        self.assertEqual(len(new_dataset_schema['labels']), 1)
        print(new_dataset_metadata)

        print('\nTest 3.1 ok')

    def test_04_get_version_schema(self):
        print('4.1 get_version_schema')

        dataset_metadata, dummy = post_dataset_metadata(
            'test dataset',
            'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
            'description of the dataset',
            'Fred',
        )

        version_metadata, version_schema = post_version_metadata(dataset_metadata, 1)

        labels_list = [
            {
                'type': 'LabelAnnotation',
                'label': 'label1',
                'value': 'value1',
                'active': True,
            }
        ]

        new_dataset_metadata, dummy = patch_dataset_metadata(
            dataset_metadata, description='new description', labels=labels_list
        )

        new_version_schema = get_version_schema(new_dataset_metadata, version_metadata)

        self.assertEqual(len(version_schema['labels']), 0)
        print(version_schema)
        self.assertEqual(len(new_version_schema['labels']), 1)
        print(new_version_schema)

        print('\nTest 4.1 ok')

    def test_05_patch_version_metadata(self):
        print('5.1 patch_version_metadata')

        dataset_metadata, dummy = post_dataset_metadata(
            'test dataset',
            'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
            'first description',
            'Fred',
        )

        version_metadata, version_schema = post_version_metadata(dataset_metadata, 1)

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
        annotation = ServiceExecutionAnnotation(
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

        annotations_list = annotation.to_dict()

        new_version_metadata, new_version_schema = patch_version_metadata(
            dataset_metadata, version_metadata, annotations=annotations_list
        )

        self.assertEqual(len(version_metadata['annotations']), 0)
        self.assertEqual(len(new_version_metadata['annotations']), 1)
        self.assertEqual(len(version_schema['fields']), 0)
        self.assertEqual(len(new_version_schema['fields']), 2)
        self.assertEqual(len(new_version_schema['required']), 1)
        print(new_version_schema)
        print(new_version_metadata)

        print('\nTest 5.1 ok')

    def test_06_get_travelling_metadata(self):
        print('6.1 get_travelling_metadata')

        labels_list = [
            {
                'type': 'LabelAnnotation',
                'label': 'label1',
                'value': 'value1',
                'active': True,
            }
        ]

        dataset_metadata, dummy = post_dataset_metadata(
            'test dataset',
            'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
            'first description',
            'Fred',
            labels=labels_list,
        )

        self.assertEqual(dataset_metadata['synchronised_datetime'], _DEFAULT_SYNC_TIME)

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
        annotation = ServiceExecutionAnnotation(
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

        annotations_list = annotation.to_dict()

        version_metadata, dummy = post_version_metadata(
            dataset_metadata, 1, annotations=annotations_list
        )

        print(dataset_metadata)

        travelling_metadata, travelling_schema = get_travelling_metadata(
            dataset_metadata, version_metadata
        )

        self.assertEqual(len(travelling_metadata['annotations']), 1)
        self.assertEqual(len(travelling_metadata['labels']), 1)
        self.assertEqual(travelling_metadata['dataset_version'], 1)
        self.assertNotEqual(
            travelling_metadata['synchronised_datetime'], _DEFAULT_SYNC_TIME
        )
        self.assertEqual(len(travelling_schema['labels']), 1)
        self.assertEqual(len(travelling_schema['fields']), 2)
        self.assertEqual(len(travelling_schema['required']), 1)
        print(travelling_schema)
        print(travelling_metadata)

        print('\nTest 6.1 ok')

    def test_07_post_travelling_metadata_to_new_dataset(self):
        print('7.1 post_travelling_metadata_to_new_dataset')

        labels_list = [
            {
                'type': 'LabelAnnotation',
                'label': 'label1',
                'value': 'value1',
                'active': True,
            }
        ]

        dataset_metadata, dummy = post_dataset_metadata(
            'test dataset',
            'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
            'first description',
            'Fred',
            labels=labels_list,
        )

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
        annotation = ServiceExecutionAnnotation(
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

        annotations_list = annotation.to_dict()

        version_metadata, dummy = post_version_metadata(
            dataset_metadata, 1, annotations=annotations_list
        )

        travelling_metadata, dummy = get_travelling_metadata(
            dataset_metadata, version_metadata
        )

        (
            new_dataset,
            new_dataset_schema,
            new_version,
            new_schema,
        ) = post_travelling_metadata_to_new_dataset(travelling_metadata, 2)

        print(new_dataset)
        print(new_dataset_schema)
        print(new_version)
        print(new_schema)

        self.assertEqual(len(new_dataset['annotations']), 0)
        self.assertEqual(len(new_dataset['labels']), 1)
        self.assertEqual(new_dataset['synchronised_datetime'], _DEFAULT_SYNC_TIME)
        self.assertEqual(len(new_dataset_schema['labels']), 1)
        self.assertEqual(len(new_version['annotations']), 1)
        self.assertEqual(len(new_version['labels']), 0)
        self.assertEqual(new_version['dataset_version'], 2)
        self.assertEqual(new_version['synchronised_datetime'], _DEFAULT_SYNC_TIME)
        self.assertEqual(len(new_schema['labels']), 1)
        self.assertEqual(len(new_schema['fields']), 2)
        self.assertEqual(len(new_schema['required']), 1)

        print('\nTest 7.1 ok')

    def test_08_patch_travelling_metadata_to_existing_dataset(self):
        print('8.1 patch_travelling_metadata_to_existing_dataset')

        labels_list = [
            {
                'type': 'LabelAnnotation',
                'label': 'label1',
                'value': 'value1',
                'active': True,
            }
        ]

        dataset_metadata, dummy = post_dataset_metadata(
            'test dataset',
            'dataset-0d7ce92a-50ff-42f4-9936-6ccf701938c1',
            'first description',
            'Fred',
            labels=labels_list,
        )

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
        annotation = ServiceExecutionAnnotation(
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

        annotations_list = annotation.to_dict()

        version_metadata, dummy = post_version_metadata(
            dataset_metadata, 1, annotations=annotations_list
        )

        travelling_metadata, dummy = get_travelling_metadata(
            dataset_metadata, version_metadata
        )

        self.assertEqual(len(travelling_metadata['labels']), 1)

        # Push dictionary to file to test the download/upload
        with open('testfile.meta', "w", encoding='utf8') as meta_file:
            json.dump(travelling_metadata, meta_file)

        labels2_list = [
            {
                'type': 'LabelAnnotation',
                'label': 'label2',
                'value': 'value2',
                'active': True,
            }
        ]

        # Patch a label to the travelling metadata
        with open('testfile.meta', "r", encoding='utf8') as meta_file:
            new_travelling_metadata, dummy = patch_travelling_metadata(
                json.load(meta_file), labels=labels2_list
            )
            self.assertEqual(len(new_travelling_metadata['labels']), 2)

        # Patch a label to the original metadata
        labels3_list = [
            {
                'type': 'LabelAnnotation',
                'label': 'label3',
                'value': 'value3',
                'active': True,
            }
        ]

        new_dataset_metadata, dummy = patch_dataset_metadata(
            dataset_metadata, labels=labels3_list
        )
        self.assertEqual(len(new_dataset_metadata['labels']), 2)

        (
            existing_dataset,
            existing_schema,
            new_version,
            new_schema,
        ) = post_travelling_metadata_to_existing_dataset(
            new_travelling_metadata, new_dataset_metadata, 2
        )

        print(existing_dataset)
        print(existing_schema)
        print(new_version)
        print(new_schema)

        self.assertEqual(len(existing_dataset['annotations']), 0)
        self.assertEqual(len(existing_dataset['labels']), 3)
        self.assertEqual(existing_dataset['synchronised_datetime'], _DEFAULT_SYNC_TIME)
        self.assertEqual(len(existing_schema['labels']), 3)
        self.assertEqual(len(new_version['annotations']), 1)
        self.assertEqual(len(new_version['labels']), 0)
        self.assertEqual(new_version['dataset_version'], 2)
        self.assertEqual(new_version['synchronised_datetime'], _DEFAULT_SYNC_TIME)
        self.assertEqual(len(new_schema['labels']), 3)
        self.assertEqual(len(new_schema['fields']), 2)
        self.assertEqual(len(new_schema['required']), 1)

        print('\nTest 8.1 ok')

    def test_20_smina_annotation_no_existing_metadata(self):
        print('20 smina annotation no existing metadata')
        proj_dir = 'test/output/api/20/'
        if not os.path.isdir(proj_dir):
            os.makedirs(proj_dir)

        # Normally the application spec comes from the instance record in the Data Tier
        # However it's possible to use the original yaml for testing
        # with open('test/input/virtual-screening.yaml', 'rt') as yaml_file:
        #     yaml_dict = safe_load(yaml_file)
        #     job_application_spec = yaml_dict['jobs']['run-smina']

        job_application_spec = {
            "collection": "im-rdkit-virtual-screening",
            "job": "run-smina",
            "version": "1.0.0",
            "variables": {
                "ligand": "dhfr-ligand.mol",
                "ligands": "candidates-10.sdf",
                "protein": "dhfr-receptor-ph7.pdb",
                "boxPadding": 4,
                "exhaustiveness": 8,
                "scoringFunction": "vina",
            },
        }

        job_rendered_spec = {
            'collection': 'im-virtual-screening',
            'job': 'run-smina',
            'version': '1.0.0',
            'image': 'informaticsmatters/vs-nextflow:latest',
            'type': 'NEXTFLOW',
            'projectMount': '/data',
            'workingDirectory': '/data',
            'command': "nextflow -log .instance-e83457e7-5995-4d96-9ebd-00eba831fe89/nextflow.log run /code/smina-docking.nf --ligands 'candidates-10.sdf' --protein 'dhfr-receptor-ph7.pdb' --ligand 'dhfr-ligand.mol' --padding 4 --exhaustiveness 8 --scoring_function 'vina' --publish_dir './' --output_basename 'results_smina' -with-trace .instance-e83457e7-5995-4d96-9ebd-00eba831fe89/trace.txt -with-report .instance-e83457e7-5995-4d96-9ebd-00eba831fe89/report.html",
            'outputs': {
                'dockedSDF': {
                    'title': 'Docked poses',
                    'mime-types': ['chemical/x-mdl-sdfile'],
                    'creates': './/results_smina.sdf',
                    'type': 'file',
                    'annotation-properties': {
                        'fields-descriptor': {
                            'origin': 'squonk2-job',
                            'description': 'Run smina docking',
                            'fields': {
                                'minimizedAffinity': {
                                    'type': 'number',
                                    'description': 'Binding affinity predicted by smina docking',
                                    'required': True,
                                    'active': True,
                                }
                            },
                        },
                        'service-execution': {
                            'service_ref': 'https://discourse.squonk.it/t/job-run-smina/78'
                        },
                        'derived-from': 'ligands',
                    },
                }
            },
            'debug': True,
        }

        written_files = create_job_annotations(
            proj_dir, job_application_spec, job_rendered_spec, 'testuser', False
        )

        self.assertEqual(len(written_files), 2)

        # The results metadata file is: results_smina.meta.json
        results_metadata_path = os.path.join(proj_dir, 'results_smina.meta.json')

        with open(results_metadata_path, 'rt', encoding='utf8') as meta_file:
            results_metadata = json.load(meta_file)
            self.assertEqual(results_metadata['dataset_name'], 'ligands')
            self.assertEqual(len(results_metadata['annotations']), 1)

        print('\nTest 20 ok')

    def test_21_smina_annotation_with_existing_metadata(self):
        # In this case we need to create metadata for the file in the derived-from field
        # and then add the service execution annotation

        print('21 smina annotation with existing metadata')
        proj_dir = 'test/output/api/21/'
        if not os.path.isdir(proj_dir):
            os.makedirs(proj_dir)

        dataset_metadata, dummy = post_dataset_metadata(
            'candidates-10.sdf',
            'none',
            'Metadata created by test for candidates-10.sdf',
            'testuser',
        )

        version_metadata, dummy = post_version_metadata(dataset_metadata, 1)

        travelling_metadata, dummy = get_travelling_metadata(
            dataset_metadata, version_metadata
        )

        # The derived-from "ligands" file is: candidates-10.sdf
        travelling_metadata_path = os.path.join(proj_dir, 'candidates-10.meta.json')

        with open(travelling_metadata_path, 'wt', encoding='utf8') as meta_file:
            json.dump(travelling_metadata, meta_file)

        job_application_spec = {
            "collection": "im-rdkit-virtual-screening",
            "job": "run-smina",
            "version": "1.0.0",
            "variables": {
                "ligand": "dhfr-ligand.mol",
                "ligands": "candidates-10.sdf",
                "protein": "dhfr-receptor-ph7.pdb",
                "boxPadding": 4,
                "exhaustiveness": 8,
                "scoringFunction": "vina",
            },
        }

        job_rendered_spec = {
            'collection': 'im-virtual-screening',
            'job': 'run-smina',
            'version': '1.0.0',
            'image': 'informaticsmatters/vs-nextflow:latest',
            'type': 'NEXTFLOW',
            'projectMount': '/data',
            'workingDirectory': '/data',
            'command': "nextflow -log .instance-e83457e7-5995-4d96-9ebd-00eba831fe89/nextflow.log run /code/smina-docking.nf --ligands 'candidates-10.sdf' --protein 'dhfr-receptor-ph7.pdb' --ligand 'dhfr-ligand.mol' --padding 4 --exhaustiveness 8 --scoring_function 'vina' --publish_dir './' --output_basename 'results_smina' -with-trace .instance-e83457e7-5995-4d96-9ebd-00eba831fe89/trace.txt -with-report .instance-e83457e7-5995-4d96-9ebd-00eba831fe89/report.html",
            'outputs': {
                'dockedSDF': {
                    'title': 'Docked poses',
                    'mime-types': ['chemical/x-mdl-sdfile'],
                    'creates': './/results_smina.sdf',
                    'type': 'file',
                    'annotation-properties': {
                        'fields-descriptor': {
                            'origin': 'squonk2-job',
                            'description': 'Run smina docking',
                            'fields': {
                                'minimizedAffinity': {
                                    'type': 'number',
                                    'description': 'Binding affinity predicted by smina docking',
                                    'required': True,
                                    'active': True,
                                }
                            },
                        },
                        'service-execution': {
                            'service_ref': 'https://discourse.squonk.it/t/job-run-smina/78'
                        },
                        'derived-from': 'ligands',
                    },
                }
            },
            'debug': True,
        }

        written_files = create_job_annotations(
            proj_dir, job_application_spec, job_rendered_spec, 'testuser', False
        )

        self.assertEqual(len(written_files), 2)

        # The results metadata file is: results_smina.meta.json
        results_metadata_path = os.path.join(proj_dir, 'results_smina.meta.json')
        with open(results_metadata_path, 'rt', encoding='utf8') as meta_file:
            results_metadata = json.load(meta_file)
            self.assertEqual(results_metadata['dataset_name'], 'candidates-10.sdf')
            self.assertEqual(len(results_metadata['annotations']), 1)

        print('\nTest 21 ok')

    def test_22_fragstein_annotation_no_existing_metadata(self):
        print('22 fragstein annotation no existing metadata')
        proj_dir = 'test/output/api/22/'
        if not os.path.isdir(proj_dir):
            os.makedirs(proj_dir)

        # with open('test/input/test.yaml', 'rt') as yaml_file:
        #     yaml_dict = safe_load(yaml_file)
        #     job_application_spec = yaml_dict['jobs']['fragmenstein-combine']

        job_application_spec = {
            "collection": "fragmenstein",
            "job": "fragmenstein-combine",
            "version": "1.0.0",
            "variables": {
                "fragments": ["CD44MMA-x0017_0A.mol", "CD44MMA-x0022_0A.mol"],
                "protein": "CD44MMA-x0017_0A_apo-desolv.pdb",
                "outfile": "tim-merged.sdf",
                "count": 2,
                "removeHydrogens": True,
            },
        }

        job_rendered_spec = {
            "collection": "fragmenstein",
            "job": "fragmenstein-combine",
            "version": "1.0.0",
            "image": "registry.gitlab.com/informaticsmatters/squonk-fragmenstein:stable",
            "type": "SIMPLE",
            "projectMount": "/data",
            "workingDirectory": "/data",
            "command": "/code/merger.py --fragments 'CD44MMA-x0017_0A.mol' 'CD44MMA-x0022_0A.mol' --protein 'CD44MMA-x0017_0A_apo-desolv.pdb' --outfile '.instance-3d97bcbe-e462-4bbc-bef7-f6fd57803a16/tim-merged.sdf' --count 2 --remove-hydrogens --work-dir .instance-3d97bcbe-e462-4bbc-bef7-f6fd57803a16/output",
            "outputs": {
                "outputs": {
                    "title": "Merged molecules",
                    "mime-types": ["chemical/x-mdl-sdfile"],
                    "creates": "tim-merged.sdf",
                    "type": "file",
                    "annotation-properties": {
                        "fields-descriptor": {
                            "origin": "squonk2-job",
                            "description": "Fragmenstein combine",
                            "fields": {
                                "ID": {
                                    "type": "string",
                                    "description": "Molecule ID",
                                    "required": True,
                                },
                                "DDG": {
                                    "type": "number",
                                    "description": "Delta deta G",
                                    "required": True,
                                },
                                "RMSD": {
                                    "type": "number",
                                    "description": "RMSD from input fragments",
                                    "required": True,
                                },
                            },
                        },
                        "service-execution": {
                            "service_ref": "https://discourse.squonk.it/t/job-fragmenstein/110"
                        },
                        "derived-from": "fragments",
                    },
                }
            },
        }

        print(job_application_spec)
        print(job_rendered_spec)

        written_files = create_job_annotations(
            proj_dir, job_application_spec, job_rendered_spec, 'testuser', False
        )

        self.assertEqual(len(written_files), 2)

        # The results metadata file is: tim-merged.meta.json
        results_metadata_path = os.path.join(proj_dir, 'tim-merged.meta.json')
        with open(results_metadata_path, 'rt', encoding='utf8') as meta_file:
            results_metadata = json.load(meta_file)
            self.assertEqual(results_metadata['dataset_name'], 'fragments')
            self.assertEqual(len(results_metadata['annotations']), 1)

        print('\nTest 22 ok')

    def test_23_fragstein_annotation_no_existing_metadata_fields(self):
        print('23 fragstein annotation no existing metadata fields')
        proj_dir = 'test/output/api/24/'
        if not os.path.isdir(proj_dir):
            os.makedirs(proj_dir)

        # with open('test/input/test.yaml', 'rt') as yaml_file:
        #     yaml_dict = safe_load(yaml_file)
        #     job_application_spec = yaml_dict['jobs']['fragmenstein-combine']

        job_application_spec = {
            "collection": "fragmenstein",
            "job": "fragmenstein-combine",
            "version": "1.0.0",
            "variables": {
                "fragments": ["CD44MMA-x0017_0A.mol", "CD44MMA-x0022_0A.mol"],
                "protein": "CD44MMA-x0017_0A_apo-desolv.pdb",
                "outfile": "tim-merged.sdf",
                "count": 2,
                "removeHydrogens": True,
            },
        }

        job_rendered_spec = {
            "collection": "fragmenstein",
            "job": "fragmenstein-combine",
            "version": "1.0.0",
            "image": "registry.gitlab.com/informaticsmatters/squonk-fragmenstein:stable",
            "type": "SIMPLE",
            "projectMount": "/data",
            "workingDirectory": "/data",
            "command": "/code/merger.py --fragments 'CD44MMA-x0017_0A.mol' 'CD44MMA-x0022_0A.mol' --protein 'CD44MMA-x0017_0A_apo-desolv.pdb' --outfile '.instance-3d97bcbe-e462-4bbc-bef7-f6fd57803a16/tim-merged.sdf' --count 2 --remove-hydrogens --work-dir .instance-3d97bcbe-e462-4bbc-bef7-f6fd57803a16/output",
            "outputs": {
                "outputs": {
                    "title": "Merged molecules",
                    "mime-types": ["chemical/x-mdl-sdfile"],
                    "creates": "tim-merged.sdf",
                    "type": "file",
                    "annotation-properties": {
                        "fields-descriptor": {
                            "origin": "squonk2-job",
                            "description": "Fragmenstein combine",
                            "fields": {
                                "ID": {
                                    "type": "string",
                                    "description": "Molecule ID",
                                    "required": True,
                                },
                                "DDG": {
                                    "type": "number",
                                    "description": "Delta deta G",
                                    "required": True,
                                },
                                "RMSD": {
                                    "type": "number",
                                    "description": "RMSD from input fragments",
                                    "required": True,
                                },
                            },
                        },
                        "service-execution": {
                            "service_ref": "https://discourse.squonk.it/t/job-fragmenstein/110"
                        },
                        "derived-from": "fragments",
                    },
                }
            },
        }

        print(job_application_spec)
        print(job_rendered_spec)

        written_files = create_job_annotations(
            proj_dir, job_application_spec, job_rendered_spec, 'testuser', True
        )

        self.assertEqual(len(written_files), 3)

        # The results params file is: tim-merged.params.json
        results_params_path = os.path.join(proj_dir, 'tim-merged.params.json')
        with open(results_params_path, 'rt', encoding='utf8') as params_file:
            results_params = json.load(params_file)
            self.assertEqual(len(results_params), 3)

        print('\nTest 23 ok')

    # def test_24_smina_annotation_with_existing_metadata(self):
    #     # Similar to 20 but using the library to render the rendered_spec
    #
    #     print('24 smina annotation with existing metadata')
    #     proj_dir = 'test/output/api/21/'
    #     if not os.path.isdir(proj_dir):
    #         os.makedirs(proj_dir)
    #
    #     dataset_metadata, dummy = post_dataset_metadata(
    #         'candidates-10.sdf',
    #         'none',
    #         'Metadata created by test for candidates-10.sdf',
    #         'testuser',
    #     )
    #
    #     version_metadata, dummy = post_version_metadata(dataset_metadata, 1)
    #
    #     travelling_metadata, dummy = get_travelling_metadata(
    #         dataset_metadata, version_metadata
    #     )
    #
    #     # The derived-from "ligands" file is: candidates-10.sdf
    #     travelling_metadata_path = os.path.join(proj_dir, 'candidates-10.meta.json')
    #
    #     with open(travelling_metadata_path, 'wt', encoding='utf8') as meta_file:
    #         json.dump(travelling_metadata, meta_file)
    #
    #     job_application_spec = {
    #         "collection": "im-rdkit-virtual-screening",
    #         "job": "run-smina",
    #         "version": "1.0.0",
    #         "variables": {
    #             "ligand": "dhfr-ligand.mol",
    #             "ligands": "candidates-10.sdf",
    #             "protein": "dhfr-receptor-ph7.pdb",
    #             "boxPadding": 4,
    #             "exhaustiveness": 8,
    #             "scoringFunction": "vina",
    #         },
    #     }
    #
    #     with open('test/input/virtual-screening.yaml', 'rt') as yaml_file:
    #         yaml_dict = safe_load(yaml_file)
    #         smina_job = yaml_dict['jobs']['run-smina']
    #
    #     print(smina_job['variables'])
    #     print(job_application_spec['variables'])
    #
    #     job_rendered_spec, success = decoder.decode(smina_job['variables'], job_application_spec['variables'],
    #                                               'command',
    #                                               decoder.TextEncoding.JINJA2_3_0)
    #
    #     print (job_rendered_spec)
    #     print (success)
    #     # job_rendered_spec = {
    #     #     'collection': 'im-virtual-screening',
    #     #     'job': 'run-smina',
    #     #     'version': '1.0.0',
    #     #     'image': 'informaticsmatters/vs-nextflow:latest',
    #     #     'type': 'NEXTFLOW',
    #     #     'projectMount': '/data',
    #     #     'workingDirectory': '/data',
    #     #     'command': "nextflow -log .instance-e83457e7-5995-4d96-9ebd-00eba831fe89/nextflow.log run /code/smina-docking.nf --ligands 'candidates-10.sdf' --protein 'dhfr-receptor-ph7.pdb' --ligand 'dhfr-ligand.mol' --padding 4 --exhaustiveness 8 --scoring_function 'vina' --publish_dir './' --output_basename 'results_smina' -with-trace .instance-e83457e7-5995-4d96-9ebd-00eba831fe89/trace.txt -with-report .instance-e83457e7-5995-4d96-9ebd-00eba831fe89/report.html",
    #     #     'outputs': {
    #     #         'dockedSDF': {
    #     #             'title': 'Docked poses',
    #     #             'mime-types': ['chemical/x-mdl-sdfile'],
    #     #             'creates': './/results_smina.sdf',
    #     #             'type': 'file',
    #     #             'annotation-properties': {
    #     #                 'fields-descriptor': {
    #     #                     'origin': 'squonk2-job',
    #     #                     'description': 'Run smina docking',
    #     #                     'fields': {
    #     #                         'minimizedAffinity': {
    #     #                             'type': 'number',
    #     #                             'description': 'Binding affinity predicted by smina docking',
    #     #                             'required': True,
    #     #                             'active': True,
    #     #                         }
    #     #                     },
    #     #                 },
    #     #                 'service-execution': {
    #     #                     'service_ref': 'https://discourse.squonk.it/t/job-run-smina/78'
    #     #                 },
    #     #                 'derived-from': 'ligands',
    #     #             },
    #     #         }
    #     #     },
    #     #     'debug': True,
    #     # }
    #
    #     written_files = create_job_annotations(
    #         proj_dir, job_application_spec, job_rendered_spec, 'testuser', False
    #     )
    #
    #     self.assertEqual(len(written_files), 2)
    #
    #     # The results metadata file is: results_smina.meta.json
    #     results_metadata_path = os.path.join(proj_dir, 'results_smina.meta.json')
    #     with open(results_metadata_path, 'rt', encoding='utf8') as meta_file:
    #         results_metadata = json.load(meta_file)
    #         self.assertEqual(results_metadata['dataset_name'], 'candidates-10.sdf')
    #         self.assertEqual(len(results_metadata['annotations']), 1)
    #
    #     print('\nTest 24 ok')


if __name__ == '__main__':
    unittest.main()
