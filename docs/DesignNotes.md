# Data Manager Metadata - Design Notes
The Data Manager Metadata library 
the HTTP and REST API service, Flask's **SQLAlchemy** to manage the database
and Flask's Migration (**Alembic**) to manage database migrations and
**Celery** for remote (asynchronous) task execution.

## Directory contents

-   `data_manager_metadata` contains the application (Python) code
    -   `__init__.py` standard functionality. 
    -   `metadata.py` contains the classes for the metadata class and annotations classes and all 
        'intelligence'
-   `md-manage.py` contains command line commands to create annotations
-   `docs/` is for background documentation (including this file)
-   `test/` contains the functional test set including migration tests. 
    Produces example output for each annotation type. Should be run each time the functionality 
    is changed. It is also run in github actions to build the library. 

   
## Application design

`__init__.py` and `app.py` are responsible for creating the connexion/Flask
app and creating a `db` and `migration` objects.
These objects are used by several models with the `db`
object is used by `models.py` to define the database topology
(using `SQLAlchemy`).

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

