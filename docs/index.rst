.. dataset documentation master file, created by
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

grano: facebook, for terrorists!
=========================================

.. toctree::
   :hidden:

``grano`` is a web-based framework for the storage, analysis and presentation
of social network information. Many types of interactions between people,
organisations and institutions can be understood in terms of network structures.

Such graphs provide an apt metaphor for the distribution of political, social
and economic influence. ``grano`` is aimed at journalists, activists and
researchers who want to explore and explain such structures. For example,
consider the following contexts:

* Lobby registers disclose connections between lobbyists, lobbying firms, their
  clients and political actors.
* Spending and procurement information can be understood as a graph of public
  bodies and private suppliers.
* Newspaper articles often establish narrative bridges between various actors,
  a short summary can often be given as a graph.


A toolkit for understanding networks
------------------------------------

``grano`` is not intended as a stand-alone solution to analyze all of these types 
of structures. Rather, the software can be seen as a building block that can 
help to build bespoke interfaces that ideally match the domain that needs to 
be explored. To support the analysis of such structures, ``grano`` provides a set
of services:

* A basic network data store with custom configurable schemata for any use 
  case.
* Full source tracking for all properties of entities and relations in the 
  graph.
* Canonicalization and aliasing of entities in the network ("BP" is also known
  as "British Petroleum").
* Full-text search and faceting for entities in the network.

In the future, the following additional services will be available:

* A RESTful web API to read and write graph information, and export options for
  more specific network file formats.
* A web-based property editor for graph entities and relations.
* Computation of graph metrics and aggregate reports based on entity properties.


Contents
--------

.. toctree::
   :maxdepth: 2

   technical
   install
   schema
   services
   api


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

``grano`` is written and maintained by `Friedrich Lindenberg <http://pudo.org>`_.
Please feel free to contribute any improvements as pull requests on GitHub, or
create an issue to discuss them first.
