import os
import yaml
import colander
from colander import SchemaNode
from pprint import pprint
from datetime import datetime

from grano.core import db
from grano.model import Schema, Attribute
from grano.logic.validation import Invalid, database_name
from grano.logic.references import ProjectRef
from grano.logic import attributes

TYPES_VALIDATOR = colander.OneOf(Attribute.DATATYPES.keys())


class AttributeValidator(colander.MappingSchema):
    name = SchemaNode(colander.String(),
                      validator=database_name)
    label = SchemaNode(colander.String(),
                       validator=colander.Length(min=3))
    description = SchemaNode(colander.String(),
                             missing='', default='')
    datatype = SchemaNode(colander.String(),
                          validator=TYPES_VALIDATOR,
                          missing='string')
    hidden = SchemaNode(colander.Boolean(),
                        missing=False)


class Attributes(colander.SequenceSchema):
    attribute = AttributeValidator()


class SchemaValidator(colander.MappingSchema):
    project = SchemaNode(ProjectRef())
    name = SchemaNode(colander.String(),
                      validator=database_name)
    label = SchemaNode(colander.String(),
                       validator=colander.Length(min=3))
    label_in = SchemaNode(colander.String(),
                          missing=None, validator=colander.Length(min=3))
    label_out = SchemaNode(colander.String(),
                           missing=None, validator=colander.Length(min=3))
    hidden = SchemaNode(colander.Boolean(),
                        missing=False)
    obj = SchemaNode(colander.String(),
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
    schema.project.updated_at = datetime.utcnow()
    db.session.add(schema)

    names = []
    for attribute in data.get('attributes', []):
        attribute['schema'] = schema
        attr = attributes.save(attribute)
        schema.attributes.append(attr)
        names.append(attr.name)

    for attr in schema.attributes:
        if attr.name not in names:
            attributes.delete(attr)

    return schema


def delete(schema):
    for attr in schema.attributes:
        attributes.delete(attr)
    db.session.delete(schema)


def import_schema(project, fh):
    data = yaml.load(fh.read())
    if isinstance(data, dict):
        data = [data]
    try:
        for cur in data:
            schema = Schema.by_name(project, cur.get('name'))
            cur['project'] = project
            save(cur, schema=schema)
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
            dumped = yaml.safe_dump(schema.to_dict(schema),
                                    canonical=False,
                                    default_flow_style=False,
                                    indent=4)
            fh.write(dumped)


def check_attributes(form, value):
    """ Form validator to check that the all attribute names used
    by this schema are unused. """

    if value.get('obj') == 'relation':
        return

    for attr in value.get('attributes', []):
        q = db.session.query(Attribute)
        q = q.filter(Attribute.name == attr.get('name'))
        q = q.join(Schema)
        q = q.filter(Schema.obj == value.get('obj'))
        q = q.filter(Schema.name != value.get('name'))
        q = q.filter(Schema.project == value.get('project'))
        attrib = q.first()
        if attrib is not None:
            raise Invalid(form,
                          "Attribute '%s' already declared in schema '%s'"
                          % (attr.get('name'), attrib.schema.name))
