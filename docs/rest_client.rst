
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
