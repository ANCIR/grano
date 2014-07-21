from grano.core import db
from grano.model import Attribute, Property


def save(data):
    """ Create or update an attribute. 
    CAUTION: This does not, on its own, validate any data."""

    schema = data.get('schema')
    name = data.get('name')
    obj = Attribute.by_schema_and_name(schema, name)
    if obj is None:
        obj = Attribute()
        obj.name = name
        obj.datatype = data.get('datatype')
        obj.schema = schema

    obj.label = data.get('label')
    obj.hidden = data.get('hidden')
    obj.description = data.get('description')
    db.session.add(obj)

    return obj


def delete(attribute):
    """ Delete the attribute and all related properties. """
    q = db.session.query(Property)
    q = q.filter(Property.attribute==attribute)
    q.delete()
    db.session.delete(attribute)
