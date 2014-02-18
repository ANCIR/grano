import os
import yaml
import colander
from pprint import pprint

from grano.core import db, url_for
from grano.lib.exc import NotImplemented
from grano.model import Schema, Attribute
from grano.logic.validation import Invalid, database_name
from grano.logic.references import ProjectRef
from grano.logic import projects as projects_logic
from grano.logic import attributes



class AttributeValidator(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(),
        validator=database_name)
    label = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3))
    description = colander.SchemaNode(colander.String(),
        missing='', default='')
    hidden = colander.SchemaNode(colander.Boolean(),
        missing=False)


class Attributes(colander.SequenceSchema):
    attribute = AttributeValidator()


class SchemaValidator(colander.MappingSchema):
    project = colander.SchemaNode(ProjectRef())
    name = colander.SchemaNode(colander.String(),
        validator=database_name)
    label = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3))
    label_in = colander.SchemaNode(colander.String(),
        missing=None, validator=colander.Length(min=3))
    label_out = colander.SchemaNode(colander.String(),
        missing=None, validator=colander.Length(min=3))
    hidden = colander.SchemaNode(colander.Boolean(),
        missing=False)
    obj = colander.SchemaNode(colander.String(),
        validator=colander.OneOf(['entity', 'relation']))
    attributes = Attributes()


def save(data, schema=None):
    """ Create a schema. """

    schema_val = SchemaValidator(validator=check_attributes)
    data = schema_val.deserialize(data)

    if schema is None:
        schema = Schema()
        schema.name = data.get('name')
        schema.project = data.get('project')

    schema.label = data.get('label')
    schema.label_in = data.get('label_in') or schema.label
    schema.label_out = data.get('label_out') or schema.label

    schema.obj = data.get('obj')
    schema.hidden = data.get('hidden')
    db.session.add(schema)
    
    names = []
    for attribute in data.get('attributes', []):
        attribute['schema'] = schema
        attr = attributes.save(attribute)
        schema.attributes.append(attr)
        names.append(attr.name)

    for attr in schema.attributes:
        if attr.name not in names:
            db.session.delete(attr)

    return schema


def delete(schema):
    raise NotImplemented()


def import_schema(project, fh):
    data = yaml.load(fh.read())
    try:
        schema = Schema.by_name(project, data.get('name'))
        data['project'] = project
        save(data, schema=schema)
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
    data['obj'] = schema.obj
    data['project'] = projects_logic.to_rest_index(schema.project)
    data['api_url'] = url_for('schemata_api.view', slug=schema.project.slug, name=schema.name)
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
