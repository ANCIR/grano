import logging
import colander

from grano.core import db, url_for, celery
from grano.model import Entity, Schema
from grano.lib.exc import NotImplemented
from grano.logic import relations, schemata as schemata_logic
from grano.logic import properties as properties_logic
from grano.logic import projects as projects_logic
from grano.logic.references import ProjectRef, AccountRef, SchemaRef
from grano.plugins import notify_plugins


log = logging.getLogger(__name__)


class EntityBaseValidator(colander.MappingSchema):
    author = colander.SchemaNode(AccountRef())
    project = colander.SchemaNode(ProjectRef())
    

def validate(data):
    """ Due to some fairly weird interdependencies between the different elements
    of the model, validation of entities has to happen in three steps. """

    # a bit hacky
    data['schemata'] = data.get('schemata', []) + ['base']

    validator = EntityBaseValidator()
    sane = validator.deserialize(data)
    
    schemata_validator = colander.SchemaNode(colander.Mapping())
    schemata_node = colander.SchemaNode(SchemaRef(sane.get('project')))
    schemata_validator.add(colander.SchemaNode(colander.Sequence(),
        schemata_node, name='schemata'))

    sane.update(schemata_validator.deserialize(data))
    sane['schemata'] = list(set(sane['schemata']))

    sane['properties'] = properties_logic.validate(
        data.get('properties', []),
        sane.get('schemata'),
        name='properties')
    return sane


@celery.task
def _entity_changed(entity_id):
    """ Notify plugins about changes to an entity. """
    log.debug("Processing change in entity: %s", entity_id)
    def _handle(obj):
        obj.entity_changed(entity_id)
    notify_plugins('grano.entity.change', _handle)


def save(data, entity=None):
    """ Save or update an entity. """

    data = validate(data)
    
    if entity is None:
        entity = Entity()
        entity.project = data.get('project')
        entity.author = data.get('author')
        db.session.add(entity)

    entity.schemata = list(set(data.get('schemata')))

    prop_names = set()
    for name, prop in data.get('properties').items():
        prop_names.add(name)
        prop['name'] = name
        prop['author'] = data.get('author')
        properties_logic.save(entity, prop)

    for prop in entity.properties:
        if prop.name not in prop_names:
            prop.active = False

    db.session.flush()
    _entity_changed.delay(entity.id)    
    return entity


def delete(entity):
    raise NotImplemented()


def _merge_entities(source, target):
    """ Copy all properties and relations from one entity onto another, then 
    mark the source entity as an ID alias for the destionation entity. """

    target_active = [p.name for p in target.active_properties]
    target.schemata = list(set(target.schemata + source.schemata))

    for prop in source.properties:
        if prop.name in target_active:
            prop.active = False
        prop.entity = target
    
    for rel in source.inbound:
        # TODO: what if this relation now points at the same thing on both ends?
        rel.target = target
    
    for rel in source.outbound:
        rel.source = target
    
    source.same_as = target.id
    db.session.flush()


def apply_alias(project, author, canonical_name, alias_name):
    """ Given two names, find out if there are existing entities for one or 
    both of them. If so, merge them into a single entity - or, if only the 
    entity associated with the alias exists - re-name the entity. """

    canonical_name = canonical_name.strip()

    # Don't import meaningless aliases.
    if canonical_name == alias_name or not len(canonical_name):
        return log.info("No alias: %s", canonical_name)

    canonical = Entity.by_name(project, canonical_name)
    alias = Entity.by_name(project, alias_name)
    schema = Schema.by_name(project, 'base')
    attribute = schema.get_attribute('name')

    # Don't artificially increase entity counts.
    if canonical is None and alias is None:
        return log.info("Neither alias nor canonical exist: %s", canonical_name)

    # Rename an alias to its new, canonical name.
    if canonical is None:
        data = {
            'value': canonical_name,
            'schema': schema,
            'attribute': attribute,
            'active': True,
            'name': 'name',
            'source_url': None
        }
        properties_logic.save(alias, data)
        _entity_changed.delay(alias.id)
        return log.info("Renamed: %s -> %s", alias_name, canonical_name)

    # Already done, thanks.
    if canonical == alias:
        return log.info("Already aliased: %s", canonical_name)

    # Merge two existing entities, declare one as "same_as"
    if canonical is not None and alias is not None:
        _merge_entities(alias, canonical)
        _entity_changed.delay(canonical.id)
        return log.info("Mapped: %s -> %s", alias.id, canonical.id)


def to_index(entity):
    """ Convert an entity to a form appropriate for search indexing. """
    data = to_rest(entity)
    
    data['names'] = []
    for prop in entity.properties:
        if prop.name == 'name':
            data['names'].append(prop.value)

    return data


def to_rest_base(entity):
    data = {
        'id': entity.id,
        'project': projects_logic.to_rest_index(entity.project),
        'api_url': url_for('entities_api.view', id=entity.id),
        'same_as': entity.same_as
    }
    if entity.same_as:
        data['same_as_url'] = url_for('entities_api.view', id=entity.same_as)
    return data


def to_rest_index(entity):
    """ Convert an entity to the REST API form. """
    data = to_rest_base(entity)
    data['properties'] = {}
    for prop in entity.active_properties:
        name, prop = properties_logic.to_rest_index(prop)
        data['properties'][name] = prop
    return data


def to_rest(entity):
    """ Full serialization of the entity. """
    data = to_rest_base(entity)
    data['created_at'] = entity.created_at
    data['updated_at'] = entity.updated_at

    ss = [schemata_logic.to_rest_index(s) for s in entity.schemata]
    data['schemata'] = ss

    data['properties'] = {}
    for prop in entity.active_properties:
        name, prop = properties_logic.to_rest(prop)
        data['properties'][name] = prop

    data['inbound_relations'] = entity.inbound.count()
    if data['inbound_relations'] > 0:
        data['inbound_url'] = url_for('relations_api.index', target=entity.id)
    
    data['outbound_relations'] = entity.outbound.count()
    if data['outbound_relations'] > 0:
        data['outbound_url'] = url_for('relations_api.index', source=entity.id)
    
    return data
