from grano.core import db, url_for
from grano.model import Schema, Attribute
from grano.logic.validation import validate_schema
from grano.logic import projects as projects_logic
from grano.logic import attributes


def save(project, data):
    """ Create a schema. """

    data = validate_schema(data)
    
    name = data.get('name')
    obj = Schema.by_name(project, name)
    if obj is None:
        obj = Schema()
    obj.name = name
    obj.project = project
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
    data['hidden'] = schema.hidden
    return data


def to_rest_index(schema):
    data = to_basic(schema)
    data['project'] = projects_logic.to_rest_index(schema.project)
    data['api_url'] = url_for('schemata_api.view', name=schema.name)
    return data


def to_rest(schema):
    data = to_rest_index(schema)
    data['id'] = schema.id
    data['hidden'] = schema.hidden
    if schema.label_in:
        data['label_in'] = schema.label_in
    if schema.label_out:
        data['label_out'] = schema.label_out
    as_ = [attributes.to_rest(a) for a in schema.attributes]
    data['attributes'] = as_
    return data


def to_dict(schema):
    data = to_basic(schema)
    data['id'] = schema.id
    data['obj'] = schema.obj
    data['project'] = schema.project.slug
    data['hidden'] = schema.hidden
    data['label_in'] = schema.label_in
    data['label_out'] = schema.label_out
    data['attributes'] = [attributes.to_dict(a) for a in schema.attributes]
    return data
