.. _pyclient:

Python web client library
=========================


The interface in detail
-----------------------

Grano
+++++

.. autoclass:: granoclient.Grano
   :members: get, projects 


Projects
++++++++

.. autoclass:: granoclient.ProjectCollection
   :members: by_slug, create, query, all

.. autoclass:: granoclient.Project
   :members: 


Queries
+++++++

Queries are re-used whenever a result set needs to be paginated and filtered.

.. autoclass:: granoclient.Query
   :members: results, total, has_next, next, has_prev, prev


Exceptions
++++++++++

.. autoclass:: granoclient.GranoException

.. autoclass:: granoclient.GranoServerException
