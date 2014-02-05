from grano.core import db
from grano.model import Schema, Attribute
from grano.logic.validation import validate_schema


def save_schema(data):
    """ Create a schema. """

    data = validate_schema(data)
    
    name = data.get('name')
    obj = Schema.by_name(name)
    if obj is None:
        obj = Schema()
    obj.name = name
    obj.label = data.get('label')
    obj.label_in = data.get('label_in') or obj.label
    obj.label_out = data.get('label_out') or obj.label

    obj.obj = data.get('obj')
    obj.hidden = data.get('hidden')
    db.session.add(obj)
    
    names = []
    for attribute in data.get('attributes', []):
        attribute['schema'] = obj
        attr = save_attribute(attribute)
        obj.attributes.append(attr)
        names.append(attr.name)
    for attr in obj.attributes:
        if attr.name not in names:
            db.session.delete(attr)
    return obj


def save_attribute(data):
    schema = data.get('schema')
    name = data.get('name')
    obj = Attribute.by_name(schema, name)
    if obj is None:
        obj = Attribute()
    obj.name = name
    obj.label = data.get('label')
    obj.hidden = data.get('hidden')
    obj.description = data.get('description')
    obj.schema = schema
    db.session.add(obj)
    return obj
