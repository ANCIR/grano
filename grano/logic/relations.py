import logging

from grano.core import db, url_for, celery
from grano.model import Relation
from grano.logic import properties as properties_logic
from grano.logic import schemata as schemata_logic
from grano.logic import projects as projects_logic
from grano.plugins import notify_plugins


log = logging.getLogger(__name__)


@celery.task
def _relation_changed(relation_id):
    """ Notify plugins about changes to a relation. """
    log.warn("Processing change in relation: %s", relation_id)
    def _handle(obj):
        obj.relation_changed(relation_id)
    notify_plugins('grano.relation.change', _handle)


def save(project, author, schema, properties, source, target, update_criteria):
    """ Save or update a relation with the given properties. """

    q = db.session.query(Relation)
    q = q.filter(Relation.source_id==source.id)
    q = q.filter(Relation.target_id==target.id)
    q = q.filter(Relation.project_id==project.id)
    for name, only_active in update_criteria:
        value = properties.get(name).get('value')
        q = Relation._filter_property(q, name, value, only_active=only_active)
    obj = q.first()

    if obj is None:
        obj = Relation()
        db.session.add(obj)
        db.session.flush()
    
    # TODO: check they are not identical, but part of the same project
    obj.source = source
    obj.target = target
    obj.project = project
    obj.author = author
    obj.schema = schema
    properties_logic.set_many(obj, author, properties)
    _relation_changed.delay(obj.id)
    return obj


def to_index(relation):
    """ Convert a relation into a form appropriate for indexing within an 
    entity (ie. do not include entity data). """

    data = {
        'id': relation.id,
        'project': projects_logic.to_rest_index(relation.project),
        'source': relation.source_id,
        'target': relation.target_id,
        'schema': schemata_logic.to_index(relation.schema),
    }

    for prop in relation.active_properties:
        data[prop.name] = prop.value

    return data


def to_rest(relation):
    return to_rest_index(relation)


def to_rest_index(relation):
    props = {}
    for prop in relation.active_properties:
        name, prop = properties_logic.to_rest_index(prop)
        props[name] = prop
    return {
        'id': relation.id,
        'project': projects_logic.to_rest_index(relation.project),
        'api_url': url_for('relations_api.view', id=relation.id),
        'source_id': relation.source_id,
        'source_url': url_for('entities_api.view', id=relation.source_id),
        'target_id': relation.target_id,
        'target_url': url_for('entities_api.view', id=relation.target_id),
        'properties': props,
        'schema': schemata_logic.to_rest_index(relation.schema),
    }
