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


def save(data, relation=None):
    """ Save or update a relation with the given properties. """

    if relation is None:
        relation = Relation()
        relation.project = data.get('project')
        relation.author = data.get('author')
        db.session.add(relation)

    relation.source = data.get('source')
    relation.target = data.get('target')
    relation.schema = data.get('schema')
    properties_logic.set_many(relation, data.get('author'),
        data.get('properties'))
    db.session.flush()
    
    _relation_changed.delay(relation.id)
    return relation


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


def to_rest_base(relation):
    from grano.logic import entities as entities_logic
    return {
        'id': relation.id,
        'properties': {},
        'project': projects_logic.to_rest_index(relation.project),
        'api_url': url_for('relations_api.view', id=relation.id),
        'schema': schemata_logic.to_rest_index(relation.schema),
        'source': entities_logic.to_rest_index(relation.source),
        'target': entities_logic.to_rest_index(relation.target)
    }


def to_rest(relation):
    data = to_rest_base(relation)
    for prop in relation.active_properties:
        name, prop = properties_logic.to_rest(prop)
        data['properties'][name] = prop
    return data


def to_rest_index(relation):
    data = to_rest_base(relation)
    for prop in relation.active_properties:
        name, prop = properties_logic.to_rest_index(prop)
        data['properties'][name] = prop
    return data
