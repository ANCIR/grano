import logging
import colander

from grano.core import db, celery
from grano.model import Relation
from grano.logic import properties as properties_logic
from grano.logic.references import ProjectRef, AccountRef
from grano.logic.references import SchemaRef, EntityRef
from grano.plugins import notify_plugins


log = logging.getLogger(__name__)


class RelationBaseValidator(colander.MappingSchema):
    author = colander.SchemaNode(AccountRef())
    project = colander.SchemaNode(ProjectRef())


def validate(data, relation):
    """ Due to some fairly weird interdependencies between the different elements
    of the model, validation of relations has to happen in three steps. """

    validator = RelationBaseValidator()
    sane = validator.deserialize(data)
    project = sane.get('project')

    schema_validator = colander.SchemaNode(colander.Mapping())
    schema_validator.add(colander.SchemaNode(SchemaRef(project),
                         name='schema'))
    schema_validator.add(colander.SchemaNode(EntityRef(project=project),
                         name='source'))
    schema_validator.add(colander.SchemaNode(EntityRef(project=project),
                         name='target'))

    sane.update(schema_validator.deserialize(data))

    sane['properties'] = properties_logic.validate(
        'relation', relation, [sane.get('schema')], project,
        data.get('properties', []))
    return sane


@celery.task
def _relation_changed(relation_id, operation):
    """ Notify plugins about changes to a relation. """
    def _handle(obj):
        obj.relation_changed(relation_id, operation)
    notify_plugins('grano.relation.change', _handle)


def save(data, relation=None):
    """ Save or update a relation with the given properties. """
    data = validate(data, relation)

    operation = 'create' if relation is None else 'update'
    if relation is None:
        relation = Relation()
        relation.project = data.get('project')
        relation.author = data.get('author')
        db.session.add(relation)

    relation.source = data.get('source')
    relation.target = data.get('target')
    relation.schema = data.get('schema')

    prop_names = set()
    for name, prop in data.get('properties').items():
        prop_names.add(name)
        prop['name'] = name
        prop['author'] = data.get('author')
        properties_logic.save(relation, prop)

    for prop in relation.properties:
        if prop.name not in prop_names:
            prop.active = False

    db.session.flush()
    _relation_changed.delay(relation.id, operation)
    return relation


def delete(relation):
    """ Delete the relation and its properties. """
    db.session.delete(relation)
    _relation_changed.delay(relation.id, 'delete')
