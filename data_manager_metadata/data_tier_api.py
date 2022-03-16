"""Data Tier API.

    The interface layer between the mini-apps-data-tier repo and the
    data-manager-metadata repo.

    Note that in general

"""
from typing import  Any, Dict, Tuple
import copy
import os
from data_manager_metadata.metadata import Metadata


def get_metadata_filenames(filepath: str) -> Tuple[str, str]:
    """Return the associated metadata and schema filenames for a particular
    filepath.
    """
    _METADATA_EXT = '.meta.json'
    _SCHEMA_EXT = '.schema.json'

    assert filepath

    # Get filename stem from filepath
    # so in: 'filename.sdf.gz', we would get just 'filename'
    file_basename = os.path.basename(filepath)
    filename_stem = file_basename.split('.')[0]
    return filename_stem + _METADATA_EXT, filename_stem + _SCHEMA_EXT


# Dataset Methods
def post_dataset_metadata(dataset_name: str,
                          dataset_id: str,
                          description: str,
                          created_by: str,
                          **metadata_params: Any) \
        -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Create a metadata class at the dataset level.
    Returns a json schema that will be used for label searches at the
    dataset level.

    Args:
        dataset_name
        dataset_id
        description
        created_by
        **metadata_params (optional keyword arguments)

    Returns:
        metadata dict
        json_schema
    """

    # At dataset level only labels and property changes allowed.
    if 'annotations' in metadata_params:
        del metadata_params['annotations']

    # At dataset level, the version should not be set.
    if 'dataset_version' in metadata_params:
        del metadata_params['dataset_version']

    # Create the dictionary with the remaining parameters
    metadata = Metadata(dataset_name, dataset_id, description, created_by,
                        **metadata_params)
    return metadata.to_dict(), metadata.get_json_schema()


def post_version_metadata(dataset_metadata: Dict[str, Any],
                          version: int,
                          **metadata_params: Any) \
        -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Create a metadata class at the version level.

    Args:
        dataset metadata
        version
        **metadata_params (optional keyword arguments)

    Returns:
        metadata dict
        json_schema
    """
    # At version level only labels are not allowed.
    if 'labels' in metadata_params:
        del metadata_params['labels']

    version_metadata = Metadata(dataset_metadata['dataset_name'],
                                dataset_metadata['dataset_id'],
                                dataset_metadata['description'],
                                dataset_metadata['created_by'],
                                dataset_version=version,
                                **metadata_params)

    return version_metadata.to_dict(), \
           get_version_schema(dataset_metadata, version_metadata.to_dict())


def patch_dataset_metadata(dataset_metadata: Dict[str, Any],
                           **metadata_params: Any) \
        -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Update the metadata at the dataset level.

    The metadata_params will be limited to the following parameters:
    description
    labels

    Other types will be ignored (no error returned in this case).

    Args:
        dataset_metadata: to be updated
        **metadata_params (optional keyword arguments)

    Returns:
        metadata dict
        json_schema
    """

    metadata = Metadata(**dataset_metadata)

    if 'description' in metadata_params:
        metadata.set_description(metadata_params['description'])

    if 'labels' in metadata_params:
        metadata.add_labels(metadata_params['labels'])

    return metadata.to_dict(), metadata.get_json_schema()


def get_version_schema(dataset_metadata: Dict[str, Any],
                       version_metadata: Dict[str, Any]) \
        -> Dict[str, Any]:
    """Get the current json schema at the version level.

    Note that this must be called for each version of the dataset after
    a patch_dataset_metadata call to update the json schema with any
    inherited changed attributes from the dataset level.

    Args:
        version metedata

    Returns:
        json_schema
    """
    d_metadata = Metadata(**dataset_metadata)
    v_metadata = Metadata(**version_metadata)
    v_metadata.add_labels(d_metadata.get_labels())

    return v_metadata.get_json_schema()


def patch_version_metadata(dataset_metadata: Dict[str, Any],
                           version_metadata: Dict[str, Any],
                           **metadata_params: Any) \
        -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Update metadata at the version level.
    This is only used for updating annotations and description.

    Args:
        dataset_metadata
        version_metadata
        **metadata_params (optional keyword arguments)

    Returns:
        metadata dict
        json_schema
    """
    d_metadata = Metadata(**dataset_metadata)
    v_metadata = Metadata(**version_metadata)

    if 'description' in metadata_params:
        v_metadata.set_description(metadata_params['description'])

    if 'annotations' in metadata_params:
        v_metadata.add_annotations(metadata_params['annotations'])

    # This adds the dataset labels to the version metadata so
    # we can extract the json schema with both labels and annotations.
    schema_metadata = Metadata(**v_metadata.to_dict())
    schema_metadata.add_labels(d_metadata.get_labels())

    return v_metadata.to_dict(), schema_metadata.get_json_schema()


def get_travelling_metadata(dataset_metadata: Dict[str, Any],
                            version_metadata: Dict[str, Any]) \
        -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Returns "travelling metadata" at the version level. Travelling
    metadata is used when a dataset is added to project.

    It contains the labels from the dataset level and has
    a roll forward date set for re-synchronisation with the metadata
    in the data-tier.

    Args:
        dataset_metadata
        version_metadata

    Returns:
        travelling metadata dict
        travelling json_schema
    """

    d_metadata = Metadata(**dataset_metadata)
    v_metadata = Metadata(**version_metadata)
    d_metadata.add_annotations(v_metadata.get_annotations_dict())
    d_metadata.set_synchronised_datetime()
    d_metadata.set_dataset_version(v_metadata.get_dataset_version())
    return d_metadata.to_dict(), d_metadata.get_json_schema()


def post_travelling_metadata_to_new_dataset\
                (travelling_metadata: Dict[str, Any],
                 version: int) \
        -> Tuple[Dict[str, Any], Dict[str, Any],
                 Dict[str, Any], Dict[str, Any]]:
    """Creates dataset metadata with the results of the voyage.

    This method will be used when a completely new dataset is to be created
    from the travelling metadata.

    Args:
        travelling_metadata
        version

    Returns:
        dataset metadata
        dataset schema
        version metadata
        version json schema
    """

    d_metadata_params = \
        { 'labels': copy.deepcopy(travelling_metadata['labels'])}
    v_metadata_params = \
        { 'annotations': copy.deepcopy(travelling_metadata['annotations'])}

    dataset_metadata, dataset_schema = post_dataset_metadata(
        travelling_metadata['dataset_name'],
        travelling_metadata['dataset_id'],
        travelling_metadata['description'],
        travelling_metadata['created_by'],
        **d_metadata_params)

    version_metadata, version_schema = \
        post_version_metadata(dataset_metadata, version, **v_metadata_params)

    return dataset_metadata, \
           dataset_schema, \
           version_metadata, \
           version_schema


def patch_travelling_metadata(travelling_metadata: Dict[str, Any],
                              **metadata_params: Any) \
        -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Updates en-route "travelling metadata" at the version level.
    Note that currently, only the description, labels and annotations
    can be changed. Other values are set automatically.

    Args:
        travelling_metadata
        **metadata_params (optional keyword arguments)

    Returns:
        travelling metadata dict
        travelling json_schema
    """
    metadata = Metadata(**travelling_metadata)

    if 'description' in metadata_params:
        metadata.set_description(metadata_params['description'])

    if 'labels' in metadata_params:
        metadata.add_labels(metadata_params['labels'])

    if 'annotations' in metadata_params:
        metadata.add_annotations(metadata_params['annotations'])
        # This adds the version annotations to the dataset metadata so
        # we can extract the json schema with both labels and annotations.
        metadata.add_annotations(metadata.get_annotations_dict())

    return metadata.to_dict(), metadata.get_json_schema()


def post_travelling_metadata_to_existing_dataset\
                (travelling_metadata: Dict[str, Any],
                 dataset_metadata: Dict[str, Any],
                 version: int) \
        -> Tuple[Dict[str, Any], Dict[str, Any],
                 Dict[str, Any], Dict[str, Any]]:
    """Updates version metadata with the results of the voyage.

    Note that if the labels have changed, a get_version_schema will be required
    for all versions of the dataset to update the json schemas

    Args:
        travelling_metadata
        dataset_metadata
        dataset_version

    Returns:
        dataset metadata
        dataset schema
        version metadata
        version json schema
    """

    t_metadata = Metadata(**travelling_metadata)
    synchronised_datetime = t_metadata.get_synchronised_datetime()

    d_metadata_params = \
        { 'labels': copy.
            deepcopy(t_metadata.get_unapplied_labels(synchronised_datetime))}
    v_metadata_params = \
        { 'annotations': copy.deepcopy(travelling_metadata['annotations'])}

    dataset_metadata, dataset_schema = patch_dataset_metadata(
        dataset_metadata,
        **d_metadata_params)

    version_metadata, version_schema = \
        post_version_metadata(dataset_metadata, version, **v_metadata_params)

    return dataset_metadata, \
           dataset_schema,  \
           version_metadata, \
           version_schema
