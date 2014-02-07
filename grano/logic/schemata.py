from grano.core import db
from grano.model import Schema, Attribute
from grano.logic.validation import validate_schema
from grano.logic import attributes


def save(data):
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
        attr = attributes.save(attribute)
        obj.attributes.append(attr)
        names.append(attr.name)
    for attr in obj.attributes:
        if attr.name not in names:
            db.session.delete(attr)
    return obj


def to_basic(schema):
    return {
        'name': schema.name,
        'label': schema.label
    }


def to_index(schema):
    data = to_basic(schema)
    #data['attributes'] = [attributes.to_index(a) for a in schema.attributes]
    return data


def to_dict(schema):
    data = to_basic(schema)
    data['id'] = schema.id
    data['obj'] = schema.obj
    data['hidden'] = schema.hidden
    data['label_in'] = schema.label_in
    data['label_out'] = schema.label_out
    data['attributes'] = [attributes.to_dict(a) for a in schema.attributes]
    return data
