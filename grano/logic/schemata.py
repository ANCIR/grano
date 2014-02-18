import os
import yaml
from pprint import pprint

from grano.core import db, url_for
from grano.model import Schema, Attribute
from grano.logic.validation import Invalid, SchemaValidator
from grano.logic import projects as projects_logic
from grano.logic import attributes


def save(data):
    """ Create a schema. """

    data = validate_schema(data)
    obj = Schema.by_name(data.get('project'), data.get('name'))
    if obj is None:
        obj = Schema()

    obj.name = data.get('name')
    obj.project = data.get('project')
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


def import_schema(project, fh):
    data = yaml.load(fh.read())
    try:
        data['project'] = project
        save(data)
        db.session.commit()
    except Invalid, inv:
        pprint(inv.asdict())


def export_schema(project, path):
    if not os.path.exists(path):
        os.makedirs(path)
    for schema in Schema.all().filter_by(project=project):
        if schema.name == 'base':
            continue
        fn = os.path.join(path, schema.name + '.yaml')
        with open(fn, 'w') as fh:
            fh.write(yaml.dump(to_dict(schema)))


def validate_schema(data):
    schema = SchemaValidator(validator=check_attributes)
    return schema.deserialize(data)


def check_attributes(form, value):
    """ Form validator to check that the all attribute names used 
    by this schema are unused. """

    if value.get('obj') == 'relation':
        return

    for attr in value.get('attributes', []):
        q = db.session.query(Attribute)
        q = q.filter(Attribute.name==attr.get('name'))
        q = q.join(Schema)
        q = q.filter(Schema.obj==value.get('obj'))
        q = q.filter(Schema.name!=value.get('name'))
        attrib = q.first()
        if attrib is not None:
            raise Invalid(form,
                "Attribute '%s' already declared in schema '%s'" \
                 % (attr.get('name'), attrib.schema.name))


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
