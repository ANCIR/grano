Schemata
========

To keep ``granos`` data model adaptable to specific use cases, the 
platform allows users to define so-scalled schemata. They apply
either to entities or to relations (never both). While each relation
can only be associated with one schema, entities can combine several
schemata (e.g. they can be a company, but also a lobby register
entry).

The main task of a schema is to define a set of attributes, which 
describe what fields can be filled with data for an entity or 
relation. 


Importing and exporting schemata
--------------------------------

Schemata can be read and written via the REST API or via the command 
line. Imports via the command line are based on YAML files, which can
contain a schema specification like this (the corresponding JSON 
syntax for the REST API is left as an exercise)::

    name: person
    label: A person
    obj: entity
    hidden: no
    attributes:
      - name: first_name
        label: First name
      - name: last_name
        label: Last name
      - name: title
        label: Title
        hidden: yes

The above schema will apply to entities (``obj: entity``) and it defines
three attributes, one of which will not be shown in listings by default
(``hidden: yes``).

Similarly, a relation could be defined like this::

    name: gift
    label: A present
    label_in: Gifts received
    label_out: Gifts given
    obj: relation
    attributes:
      - name: description
        label: Description
      - name: value
        label: Value (in EUR)

Note that, since ``grano`` stores a directed graph, it is sometimes 
desirable for listings of relations to be headed by labels which reflect
the fact that they have different semantics on both ends (``label_in``
and ``label_out``). 

On the command line, each schema is expected to be stored in its own 
YAML file, which can be imported like this::

    python grano/manage.py schema_import my_schema.yaml

The reverse command, ``schema_export`` expects a directory name as its
sole argument. In the directory, one YAML file will be generated for 
each schema that is currently defined in ``grano``::

    python grano/manage.py schema_export my_schemata/


Base schema
-----------

All entities in ``grano`` are automatically associated with the
``base`` schema. This schema defines a ``name`` property which is 
used to identify entities (including the option to define aliases),
and an ``opencorporates_uri``, which is used by the OpenCorporates
service to store links to the company database.

