
Bulk loader API
===============

``grano`` has a Python-based bulk loading API that can be used to implement custom data loaders (e.g. as part of an ETL process). The interface uses a factory pattern to generate projects, entities and graphs. The following tutorial assumes that you have ``grano`` installed and configured to use a local database.


Creating a loader
-----------------

As a first step, you need to create a ``Loader`` object. A loader is related to one particular ``Project``, which will be created if it isn't already present in the database.

.. code-block:: python
    
    from grano.logic import Loader

    # This source URL will be applied to all properties without their own lineage:
    DEFAULT_SOURCE_URL = 'http://www.where-the-data-comes-from.com/'

    # Any settings (free-form dict):
    PROJECT_SETTINGS = {} 

    loader = Loader('my-project', project_label='My Project',
        project_settings=PROJECT_SETTINGS, source_url=DEFAULT_SOURCE_URL)


For the moment, the loader itself does not support creating schemata or loading them from a file. This can be done, though, using the command line:

.. code-block:: bash

    grano schema_import my-project my_entity_schema.yaml
    grano schema_import my-project my_relation_schema.yaml

For more details, see :ref:`schema`.

Note that all data loaded via the loader API will be created by the ``_system`` user. To allow further accounts to manage and modify the data, you may have to grant them permissions explicitly.


Creating entities and relations
-------------------------------

Once the loader (and project) have been initalized, you can begin to create entities and relations. Both entities and relations have so-called properties associated with them, each of which can be set individually. 

In order to update existing entities and relations (rather than duplicating them when a process is executed multiple times), the loader uses a set of properties of the entity or relation which will be considered unique. This means that if an entity or relation exist with a given value, that record will be updated - otherwise, a new one is created.

For entities, the default unique property is ``name`` (i.e. there can only be one entity with each name, which will be updated when the same name is used again). Relations, on the other hand, will always include the source and target entities. Other properties can be added as necessary. 

Let's create an entity:

.. code-block:: python 

    # Each entity has a list of schemata assciated with it:
    alice = loader.make_entity(['my_entity_schema'])

    # Set some properties. 'name' is part of the default schema
    alice.set('name', 'Alice')

    # 'age' would be part of a custom schema, e.g. 'my_entity_schema'
    alice.set('age', 42, source_url='http://en.wikipedia.org/wiki/Alice')

    # Save this entity to the database
    alice.save()

Once we create a second entity, we can then establish a relation between both:

.. code-block:: python 

    bob = loader.make_entity([])
    bob.set('name', 'Bob')
    bob.save()

    # Relations can only have a single schema
    rel = loader.make_relation('my_relation_schema', alice, bob)

    # Analogous to entities
    rel.set('my_relation_property', 'value')

    # Add a uniqueness criterion
    rel.unique('my_relation_property')

    rel.save()

Finally, we must tell the loader to actually commit the data we have given to the database:

.. code-block:: python

    loader.persist()


The interface in detail
-----------------------

Loader
++++++

.. autoclass:: grano.logic.loader.Loader
   :members: make_entity, make_relation, persist


EntityLoader
++++++++++++

.. autoclass:: grano.logic.loader.EntityLoader
   :members: set, unique, save


RelationLoader
++++++++++++++

.. autoclass:: grano.logic.loader.RelationLoader
   :members: set, unique, save
