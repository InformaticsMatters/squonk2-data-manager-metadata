# Data Manager Metadata - Design Notes
The Data Manager Metadata library has been developed to contain the intelligence for creating and 
managing the annotations that are attached to datasets in the Squonk2 Data Manager.
It can be used to create annotations that can then subsequently be uploaded to a dataset
via a file or the data manager POST/dataset/annotations API.

## Directory contents

-   `data_manager_metadata` contains the application (Python) code
    - `__init__.py` standard functionality. 
    - `metadata.py` contains the classes for the metadata class and annotations classes 
    - `data_tier_api.py` contains the interface to the data_tier. 
    - `exceptions.py` contains the exceptions when using the interface online. Exceptions are suppressed when running jobs. 
-   `md-manage.py` contains command line commands to create annotations
-   `docs/` is for background documentation (including this file)
-   `test/` contains the functional test set including migration tests and api tests. 
    Produces example output for each annotation type. Should be run each time the functionality 
    is changed. It is also run in github actions to build the library. 

   
## Migrating annotations
If the metadata or annotations classes change format, it will be necessary to also 
update the meta_data jsonb column in the dataset table in the Mini-Apps-Data-Tier, 
so that the output in the apis remains in a consistent format.

In general this can hopefully be achieved without too much dedicated code by adding
new class attributes with defaults, so that the metadata / annotations can be read out
and then recreated. 

Using this approach can also minimise the disruption caused by different versions of this 
library being used in different jobs.

## Design Decisions

