# Grano Query Language

This repository contains an experimental query language implementation for grano. It is
intended to augment the existing REST API with a more advanced way of accessing data.

Grano QL is inspired by MQL, the [Metaweb Query Language](http://wiki.freebase.com/wiki/MQL)
used to query Freebase. Its query-by-example approach seems more appropriate for a web
interface than SQL-inspired query languages such as Neo4J's [CYPHER](http://docs.neo4j.org/chunked/stable/cypher-query-lang.html)
or RDF's [SPARQL](http://www.w3.org/TR/rdf-sparql-query/).

* [MQL language reference](http://mql.freebaseapps.com/ch03.html)
* [MQL operators](http://wiki.freebase.com/wiki/MQL_operators)

**WARNING**: At this moment, the plugin does not implement authorization
checks. When enabled, it will make all data in your grano instance
accessible, regardless of permissions.


## Comments and Feedback

This document and the implementation in this repository are requests for
comments - none of the features are fixed at this point; and any
concerns by users are valuable feedback, even if they imply significant
changes to the language. 


## Submitting queries

When installed the Grano QL API endpoint is available at:

      /api/1/query

Queries can be submitted via HTTP GET or POST request. For GET requests, a JSON string is expected to be submitted in the ``query`` query string argument. POST requests are expected to carry the payload as the body, using ``application/json`` as a content type.


## Basic queries

A simple query could look like this:

    {
      "properties": {
        "name": "Barack Obama"
      },
      "id": null
    }

Which means: *get the id of the entity with the name Barack Obama.* 

All grano QL queries run against entities, although we'll see below how
they can be used to retrieve relations.

As seen above, submitting ``null`` for any field will attempt to retrieve
it. As a shortcut, a default set of fields can be retrieved using a
wildcard:

    {
      "*": null
    }

Similarly, a filter can be set by submitting a value for a given field:

    {
      "id": "xxx",
      "*": null
    }

This will retrieve the default set of fields for the entity with the
specified ``id``.


### Lists vs. object retrieval

To further specify the desired return type, empty lists can be used to signify
whether the query should return a single item or a list of items:

    {
      "schemata": {} // get the first available item
      // vs.
      "schemata": [{}] // get all available items
    }

This also applies to the root of the query object: queries can either
aim to retrieve one or many entities. This will get all entities
(pagination is used):

    [{
      "*": null
    }]


## Available fields

Based on these simple entity queries, the grano graph can be traversed.
The following fields are available:

* ``id``, ``status``, ``created_at``, ``updated_at`` as simple fields on
  entities.
* ``author`` is an account, with these properties:
  * ``login`` the login name
  * ``full_name``, ``id``, ``created_at``, ``updated_at``
* ``project`` the associated project, with these properties:
  * ``slug``, ``label``, ``id``, ``created_at``, ``updated_at``
* ``schemata`` a set of schemata, each with these properties:
  * ``name``, ``label``, ``hidden``, ``created_at``, ``updated_at``
* ``properties`` can have a set of properties defined as nested objects,
  with these properties on each:
  * ``name``, ``value``, ``source_url``, ``active``
* ``inbound`` has a list of inbound relations. Each relation has these
  fields: 
  * ``id``, ``created_at``, ``updated_at``
  * ``schema``, ``author`` and ``project``, analogous to those on entities.
  * ``source`` is an entity, with all it's properties available.
* ``outbound``, a list of outbound relations. Same as ``inbound``,
  except with a ``target`` entity instead of ``source``.

Some of the nested objects can be abbreviated when filtering, e.g. you
can filter for ``{"project": "test"}`` instead of ``{"project": {"slug":
"test"}}``. This applies to schemata names, author logins and property
values.

## Discussion

What's cool about this type of query:

* Readable JSON, easily constructed by a web frontend application. 
* Resembles the representation in the REST API; query and result are basically the same thing.
* Granular access to individual properties, or constellations of objects.

Potential Problems:

* How do we tell the difference between null as in "return this value" and null as in "this property is null"?


## Indexes

CREATE INDEX dbg1 ON grano_entity (project_id);
CREATE INDEX dbg2 ON grano_entity_schema (entity_id);
CREATE INDEX dbg3 ON grano_entity (id);
