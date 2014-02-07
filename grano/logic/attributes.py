from grano.core import db
from grano.model import Attribute


def save(data):
    """ Create or update an attribute. 
    CAUTION: This does not, on its own, validate any data."""

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


def to_index(attribute):
    return {
        'name': attribute.name,
        'label': attribute.label
    }


def to_rest(attribute):
    data = to_index(attribute)
    data['id'] = attribute.id
    data['hidden'] = attribute.hidden
    if attribute.description:
        data['description'] = attribute.description
    return data


def to_dict(attribute):
    data = to_index(attribute)
    data['id'] = attribute.id
    data['hidden'] = attribute.hidden
    data['description'] = attribute.description
    return data
