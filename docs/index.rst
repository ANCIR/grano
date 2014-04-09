
grano: facebook, for terrorists!
=========================================

.. toctree::
   :hidden:

``grano`` is a web-based framework for the storage, analysis and presentation
of social network information. The tool provides building blocks for custom, 
data-driven investigative solutions.

Many types of interactions between people, organisations and institutions can
be understood in terms of network structures. This makes for an apt metaphor
for the distribution of political, social and economic influence. ``grano`` is
aimed at journalists, activists and researchers who want to explore and explain
such structures.


What is grano used for?
-----------------------

The focus of ``grano`` is its reusabilty for a wide variety of scenarios. Currently,
the following services are based on the tool:

.. image:: _static/openinterests.png

* `OpenInterests.eu <http://openinterests.eu>`_ explores who has financial and 
  political interests in the institutions of the EU. The site combines
  information from various official databases into a unique catalogue.

* `nomenklatura <http://opennames.org>`_ is a data cleaning service that helps
  to de-duplicate and link entity names in raw data. The next version of this 
  service will be a part of ``grano``.


A toolkit for understanding networks
------------------------------------

``grano`` is not intended as a stand-alone solution. Rather, the software can be
seen as a toolkit that can help to build bespoke interfaces that ideally match the
domain that needs to be explored. To support the analysis of such structures,
``grano`` provides a set of services:

* A basic network data store with custom configurable schemata for any use 
  case.
* A rich :ref:`webapi` which can be used to query and manipulate the data.
* Full lineage tracking for all properties of entities and relations in the 
  graph.
* Canonicalization and aliasing of entities in the network ("BP" is also known
  as "British Petroleum").
* Full-text search and faceting for entities in the network.

In the future, the following additional services will be available:

* A web-based property editor for graph entities and relations.
* Computation of graph metrics and aggregate reports based on entity properties.


Contents
--------

.. toctree::
   :maxdepth: 2

   technical
   install
   schema
   plugins
   rest_api
   rest_client
   bulk_api


Related projects
----------------

The idea behind ``grano`` is not new, and a number of similar services have served
as an inspiration:

* `LittleSis <http://littlesis.org>`_, tracks people, companies and their 
  connections in the United States.
* `Poderopedia <http://poderopedia.org>`_, tracks connections between people 
  and companies in Chilean politics.
* `detective.io <http://detective.io>`_, allows journalists to build their own 
  data models for investigations, then fill them.

Many other tools are listed in the `SNA survey <https://docs.google.com/spreadsheet/ccc?key=0AplklDf0nYxWdFhmTWZUc0o0SzAzMkRuMTZCUVBVeHc&usp=drive_web#gid=0>`_, and
some analysis of the different approaches can be found on the
`Knight Labs' Untangled <http://untangled.knightlab.com/>`_ site.

``grano`` aims to fill a niche in this domain by providing an easily re-usable, 
well-documented solution that can handle bulk data imports and messy data particularly 
well.


Contributors
------------

``grano`` is a free software project hosted by `Code for Africa <http://www.codeforafrica.org/>`_.
It relies on contributions from people like you, so please contribute any improvements as pull
requests on GitHub, or create an issue to discuss them first.
