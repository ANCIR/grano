import re
import colander
from colander import Invalid

from grano.logic.references import ProjectRef
from grano.core import db
from grano.model import Schema, Attribute


FORBIDDEN = ['project', 'source', 'target', 'id', 'created_at', 'updated_at', 'author', 'author_id']
database_forbidden = colander.Function(lambda v: v not in FORBIDDEN, message="Reserved name")
database_format = colander.Regex('^[a-zA-Z][a-zA-Z0-9_]+[a-zA-Z0-9]$')
database_name = colander.All(database_format, database_forbidden)


def validate_properties(data, schemata):
    """ Compile a validator for the given set of properties, based on
    the available schemata. """
    
    schema = colander.SchemaNode(colander.Mapping(), name='root')
    for sche in schemata:
        for attr in sche.attributes:
            attrib = colander.SchemaNode(colander.Mapping(),
                name=attr.name, missing=colander.null)
            attrib.add(colander.SchemaNode(colander.String(),
                validator=colander.Length(min=1),
                default=None, missing=None, name='value'))
            attrib.add(colander.SchemaNode(colander.Boolean(),
                default=True, missing=True, name='active'))
            attrib.add(colander.SchemaNode(colander.String(),
                name='schema', preparer=lambda x: sche))

            # TODO: check this is a URL?
            attrib.add(colander.SchemaNode(colander.String(),
                missing=None, name='source_url'))

            schema.add(attrib)

    data = schema.deserialize(data)
    out = {}
    for k, v in data.items():
        if v != colander.null:
            out[k] = v
    return out
