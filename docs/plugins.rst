
Plugins
=======

The functionality of ``grano`` can be extended through plugins, which will be
called at certain points during the execution of the application. Typical 
uses for these notifications include storing the graph in an alternate form
(e.g. as raw files, in a full-text search index or in a graph database).


Enabling plugins
----------------

Plugins need to be enabled individually in the configuration file through a setting
called ``PLUGINS``. Be aware that one extension (e.g. the ElasticSearch support)
may expose multiple plugins - all of which need to be enabled for the extension to 
work correctly::

  PLUGINS = ['ui', 'es_boot', 'es_entity_indexer', 'es_project_indexer']


Exposing plugins
----------------

The plugin system is based on `stevedore <http://stevedore.readthedocs.org/en/latest/>`_, a 
Python library. To develop a plugin, you must implement one of the interfaces described 
below and then expose that implementation via your Python package's ``setup.py`` file.
In ``setup.py``, all plugins are added to the ``entry_points`` section like this::

    entry_points={
        'grano.startup': [
            'myplugin1 = mypackage.granoplugin:OnStartup'
        ],
        'grano.entity.change': [
            'myplugin2 = mypackage.granoplugin:EntityChange'
        ],
        'grano.relation.change': [
            'myplugin3 = mypackage.granoplugin:RelationChange'
        ],
        'grano.project.change': [
            'myplugin4 = mypackage.granoplugin:ProjectChange'
        ]
    }


The interface in detail
-----------------------

The following plugin interfaces are currently available and can be subclassed to 
hook into a specific part of the system:

System startup
++++++++++++++

.. autoclass:: grano.interface.Startup
   :members: configure


Entity changes
++++++++++++++

.. autoclass:: grano.interface.EntityChangeProcessor
   :members: entity_changed


Relation changes
++++++++++++++++

.. autoclass:: grano.interface.RelationChangeProcessor
   :members: relation_changed


Project changes
+++++++++++++++

.. autoclass:: grano.interface.ProjectChangeProcessor
   :members: project_changed
