Services
========

``grano`` includes a set of services that can be used to perform administrative tasks. Many 
of these are activated via the command line script, ``grano/manage.py``.


Sitemap generation
------------------

To improve search indexing, ``grano`` can generate a `sitemap.xml <http://www.sitemaps.org/>`_
file to assist search engines in finding relevant content. Unfortunately, sitemaps can only 
contain 50,000 entries at once. The generator thus uses the degree of the entities to explore
the most deeply linked once - essentially as indexing seeds.

To use the service, make sure the variable ``ENTITY_VIEW_PATTERN`` is set in your settings
file such that replacing ``%s`` will yield a valid URI for each entity. Then, simply run::

    grano sitemap

The generated file will be located in ``grano/static/sitemap.xml``, which ``robots.txt`` 
points towards.
