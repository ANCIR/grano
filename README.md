## Grano

Grano is currently being developed as a backend to openinterests.eu.
Please check that repository for more information about the project.


### Domain model

All
* created_at
* updated_at
* id  

Schema
* slug
* label
* obj (enum: Entity, Relation)
  
Attribute
* name
* label
* description
* schema_id

Value
* obj_id (either an Entity's or Relation's UUID)
* name
* value
* schema_id
* source_url
* active
* alias

Entity (UUID)
* [n Value]
* [n:n Schema]

Relation (UUID)
* [n Value]
* schema_id


