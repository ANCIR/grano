.. _pyclient:

Python web client library
=========================

``grano`` is extended by a comprehensive Python client library that can be used to edit projects, data schemata, entities and their relations remotely:

.. code-block:: python

    import granoclient
    
    client = granoclient.Grano()
    for project in client.projects:
        print project.label

    project = client.get('my-project')
    project.label = 'New title'
    project.save()

    data = {'schemata': ['base'], 'properties': {'name': {'value': 'Alice'}}}
    alice = project.entities.create(data)

    data = {'schemata': ['base'], 'properties': {'name': {'value': 'Bob'}}}
    bob = project.entities.create(data)

    rel = {'schema': 'my-schema', 'source': alice, 'target': bob, 'properties': {}}
    project.relations.create(rel)

    query = project.entities.query().filter('properties-name', 'Alice')
    for entity in query:
        print entity.properties.get('name').get('value')


Installation
------------

The easiest way to install the client is via the Python package index and pip/easy_install:

.. code-block:: bash

    pip install grano-client

If you want to develop the client library's code, check out the `repository <http://github.com/pudo/grani-client>`_ and set up dependencies etc. with the command:

.. code-block:: bash

    python setup.py develop

``grano-client`` depends on `requests <http://requests.readthedocs.org/en/latest/>`_ newer than 2.2.


Configuration
-------------

Several aspects of ``grano-client`` can be configured, including the host name of the ``grano`` server and the API key that is to be used for authentication. To determine these settings, the library will evaluate the following configuration sources in given order:

1. Read the ``~/.grano.ini`` file in the user's home directory. The file is a simple .ini configuration as detailed below.
2. Check the contents of the following environment variables: ``GRANO_HOST``, ``GRANO_APIKEY``.
3. Evaluate the keyword arguments passed into the constructor of ``granoclient.Grano``.

A simple configuration file for ``grano-client`` might look like this:

.. code-block:: ini

    [client]
    host = http://beta.grano.cc

    # see user profile in grano:
    api_key = xxxxxxxxxxxxxxx


The interface in detail
-----------------------

Grano
+++++

.. autoclass:: granoclient.Grano
   :members: get, projects, entities, relations


Projects
++++++++

.. autoclass:: granoclient.ProjectCollection
   :members: by_slug, create, query, all

.. autoclass:: granoclient.Project
   :members: save, reload, schemata, entities, relations


Schemata
++++++++

.. autoclass:: granoclient.SchemaCollection
   :members: by_name, create, query, all

.. autoclass:: granoclient.Schema
   :members: save, reload


Entities
++++++++

.. autoclass:: granoclient.EntityCollection
   :members: by_id, create, query, all

.. autoclass:: granoclient.Entity
   :members: save, reload, project, inbound, outbound


Relations
+++++++++

.. autoclass:: granoclient.RelationCollection
   :members: by_id, create, query, all

.. autoclass:: granoclient.Relation
   :members: save, reload, project, source, target


Queries
+++++++

Queries are re-used whenever a result set needs to be paginated and filtered.

.. autoclass:: granoclient.Query
   :members: results, total, filter, has_next, next, has_prev, prev


Exceptions
++++++++++

.. autoclass:: granoclient.GranoException

.. autoclass:: granoclient.GranoServerException

.. autoclass:: granoclient.NotFound

.. autoclass:: granoclient.InvalidRequest
