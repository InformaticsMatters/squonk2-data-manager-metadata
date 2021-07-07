Informatics Matters Data-Manager Metadata
=========================================

A metadata framework package for the Data Tier Data Manager service.
The ``im-data-manager-metadata`` package is a set of utilities
employed by the `Informatics Matters`_ Data-Manager service
as a metadata framework for molecular datasets.

.. image:: docs/data-manager-metadata.png
  :width: 1000
  :alt: Data Manager Metadata Classes


Dependencies
************
- PyYAML>=5.3
- jsonpickle>=2.0.0


Running the Unit Tests
**********************

    >>> python -m venv ~/.venv/data-manager-metadata
    >>> source ~/.venv/data-manager-metadata/bin/activate
    >>> pip install --upgrade pip
    >>> pip install -r package-requirements.txt
    >>> python -m unittest test.test



Running the Command Line Interface *md-manage.py*
*************************************************

The data manager metadata command line interface can be used by applications to
add annotations to the Metadata by means of an annotations.json files that can be
uploaded.



.. _Informatics Matters: http://www.informaticsmatters.com
