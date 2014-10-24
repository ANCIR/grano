import os
import yaml
import colander
from colander import SchemaNode
from pprint import pprint
from datetime import datetime

from grano.core import db, celery
from grano.model import Schema, Attribute
from grano.model.schema import ENTITY_DEFAULT, RELATION_DEFAULT
from grano.logic.validation import Invalid, database_name
from grano.logic.references import ProjectRef, SchemaRef
from grano.plugins import notify_plugins
from grano.logic import attributes

TYPES_VALIDATOR = colander.OneOf(Attribute.DATATYPES.keys())
DEFAULTS = {
    'entity': ENTITY_DEFAULT,
    'relation': RELATION_DEFAULT
}


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
    hidden = SchemaNode(colander.Boolean(),
                        missing=False)
    obj = SchemaNode(colander.String(),
                     validator=colander.OneOf(['entity', 'relation']))
    meta = SchemaNode(colander.Mapping(unknown='preserve'),
                      missing={})
    attributes = Attributes()


def validate(data):
    """ Validate the incoming data. """
    sane = SchemaValidator().deserialize(data)
    sref = SchemaRef(sane.get('project'))
    sane['parent'] = sref.decode(None, data.get('parent'))
    return sane


def save(data, schema=None):
    """ Create a schema. """
    data = validate(data)

    operation = 'create' if schema is None else 'update'
    if schema is None:
        schema = Schema()
        schema.name = data.get('name')
        schema.project = data.get('project')

    schema.label = data.get('label')
    schema.obj = data.get('obj')
    schema.hidden = data.get('hidden')
    schema.meta = data.get('meta')
    schema.parent = data.get('parent')

    if schema.name in DEFAULTS.values():
        schema.parent = None
    elif schema.parent is None or schema.is_circular():
        schema.parent = Schema.by_name(schema.project,
                                       DEFAULTS.get(schema.obj))

    schema.project.updated_at = datetime.utcnow()
    db.session.add(schema)

    inherited = [a.name for a in schema.inherited_attributes]
    names = []

    for attribute in data.get('attributes', []):
        if attribute.get('name') in inherited:
            continue
        attribute['schema'] = schema
        attr = attributes.save(attribute)
        schema.local_attributes.append(attr)
        names.append(attr.name)
    
    for attr in schema.local_attributes:
        if attr.name not in names:
            attributes.delete(attr)

    db.session.flush()
    _schema_changed(schema.project.slug, schema.name, operation)
    return schema


def delete(schema):
    if schema.parent is None and schema.children.count():
        return False
    _schema_changed(schema.project.slug, schema.name, 'delete')
    for child in schema.children:
        child.parent = schema.parent
    for attr in schema.local_attributes:
        attributes.delete(attr)
    db.session.delete(schema)
    return True


@celery.task
def _schema_changed(project_slug, schema_name, operation):
    """ Notify plugins about changes to a schema. """
    def _handle(obj):
        obj.schema_changed(project_slug, schema_name, operation)
    notify_plugins('grano.schema.change', _handle)


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
        fn = os.path.join(path, schema.name + '.yaml')
        with open(fn, 'w') as fh:
            dumped = yaml.safe_dump(schema.to_dict(schema),
                                    canonical=False,
                                    default_flow_style=False,
                                    indent=4)
            fh.write(dumped)
