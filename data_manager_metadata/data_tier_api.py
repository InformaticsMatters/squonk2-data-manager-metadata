"""Data Tier API.

    The interface layer between the mini-apps-data-tier repo and the
    data-manager-metadata repo.
"""
import json
from typing import  Any, Dict, Tuple
from data_manager_metadata.metadata import Metadata

# Dataset Methods

def post_dataset_metadata(dataset_name: str,
                          dataset_id: str,
                          description: str,
                          created_by: str,
                          **metadata_params) -> Dict[str, Any]:
    """Create a metadata class at the dataset level.

    Args:
        dataset_name
        dataset_id
        description
        created_by
        **metadata_params (optional keyword arguments)

    Returns:
        metadata dict
    """
    metadata = Metadata(dataset_name, dataset_id, description, created_by,
                        metadata_params)
    return metadata.to_dict()


def post_version_metadata(dataset_metadata: Dict[str, Any],
                          version: int,
                          **metadata_params: Any):
    """Create a metadata class at the version level.

    Args:
        dataset metadata
        version
        **metadata_params (optional keyword arguments)

    Returns:
        metadata json file
        json_schema json file
    """
    pass


def patch_dataset_metadata(dataset_metadata: Dict[str, Any],
                           **metadata_params: Any) -> Dict[str, Any]:
    """Update the metadata at the dataset level.

    Args:
        dataset_metadata:
        **metadata_params (optional keyword arguments)

    Returns:
        metadata
    """
    pass


def get_version_schema(dataset_metadata: Dict[str, Any],
                       version_metadataa: Dict[str, Any]) \
        -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Get the current json schema at the version level.

    Note that this must be called for each version of the dataset after
    a patch_dataset_metadata call to update the json schema with any
    inherited changed attributes from the dataset level.

    Args:
        dataset metadata
        version metedata

    Returns:
        json_schema json file
    """
    pass


def patch_version_metadata(dataset_metadata: Dict[str, Any],
                           version_metadata: Dict[str, Any],
                           **metadata_params: Any):
    """Update metadata at the version level.

    Args:
        dataset_metadata
        version_metadata
        **metadata_params (optional keyword arguments)

    Returns:
        metadata json
        json_schema json
    """
    pass


def get_travelling_metadata(dataset_metadata: Dict[str, Any],
                            version_metadata: Dict[str, Any]):
    """Returns "travelling metadata" at the version level. Travelling
    metadata is used when a dataset is added to project.

    It contains the labels from the dataset level and has
    a roll forward date set for re-synchronisation with the metadata
    in the data-tier.

    Args:
        dataset_metadata
        version_metadata

    Returns:
        travelling metadata json
        travelling json_schema json
    """
    pass


def patch_travelling_metadata(travelling_metadata: Dict[str, Any],
                              **metadata_params: Any):
    """Updates "travelling metadata" at the version level.

    Args:
        travelling_metadata
        **metadata_params (optional keyword arguments)

    Returns:
        travelling metadata json file
        travelling json_schema json file
    """
    pass


def post_travelling_metadata_to_dataset(travelling_metadata: Dict[str, Any],
                                        dataset_metadata: Dict[str, Any]):
    """Updates dataset metadata with the results of the voyage.

    Note that after this call a get_version_schema may be required
    for all versions of the dataset to update the json schema for new labels
    in combination with post_travelling_metadata_to_version below.

    Args:
        travelling_metadata
        dataset_metadata

    Returns:
        dataset metadata json
    """
    pass


def post_travelling_metadata_to_version(travelling_metadata: Dict[str, Any],
                                        dataset_metadata: Dict[str, Any],
                                        version_metadata: Dict[str, Any]):
    """Updates version metadata with the results of the voyage.

    Args:
        travelling_metadata
        dataset_metadata
        version_metadata

    Returns:
        version metadata json
        version schema json
    """
    pass
