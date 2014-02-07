import logging

from grano.core import db, url_for
from grano.model import Entity, Schema
from grano.logic import relations, schemata as schemata_logic
from grano.logic import properties as properties_logic
from grano.plugins import notify_plugins


log = logging.getLogger(__name__)


def _entity_changed(entity_id):
    """ Notify plugins about changes to an entity. """
    # TODO: put behind a queue.
    def _handle(obj):
        obj.entity_changed(entity_id)
    notify_plugins('grano.entity.change', _handle)


def save(schemata, properties, update_criteria):
    """ Save or update an entity. """
    obj = None
    if len(update_criteria):
        q = db.session.query(Entity)
        for name, only_active in update_criteria:
            value = properties.get(name).get('value')
            q = Entity._filter_property(q, name, value, only_active=only_active)
        obj = q.first()
    
    if obj is None:
        obj = Entity()
        db.session.add(obj)
        db.session.flush()
    
    obj.schemata = list(set(obj.schemata + schemata))
    properties_logic.set_many(obj, properties)
    _entity_changed(obj.id)
    return obj


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


def apply_alias(canonical_name, alias_name):
    """ Given two names, find out if there are existing entities for one or 
    both of them. If so, merge them into a single entity - or, if only the 
    entity associated with the alias exists - re-name the entity. """

    canonical_name = canonical_name.strip()

    # Don't import meaningless aliases.
    if canonical_name == alias_name or not len(canonical_name):
        return log.info("No alias: %s", canonical_name)

    canonical = Entity.by_name(canonical_name)
    alias = Entity.by_name(alias_name)
    schema = Schema.cached(Entity, 'base')

    # Don't artificially increase entity counts.
    if canonical is None and alias is None:
        return log.info("Neither alias nor canonical exist: %s", canonical_name)

    # Rename an alias to its new, canonical name.
    if canonical is None:
        properties_logic.set(alias, 'name', schema, canonical_name,
            active=True, source_url=None)
        _entity_changed(alias.id)
        return log.info("Renamed: %s", alias_name)

    # Already done, thanks.
    if canonical == alias:
        return log.info("Already aliased: %s", canonical_name)

    # Merge two existing entities, declare one as "same_as"
    if canonical is not None and alias is not None:
        _merge_entities(alias, canonical)
        _entity_changed(canonical.id)
        return log.info("Mapped: %s -> %s", alias.id, canonical.id)


def to_index(entity):
    """ Convert an entity to a form appropriate for search indexing. """

    schemata = list(entity.schemata)
    data = {
        'id': entity.id,
        'schemata': [schemata_logic.to_basic(s) for s in schemata if s.name != 'base'],
        'num_schemata': len(schemata),
        'num_properties': 0,
        'inbound': [],
        'outbound': [],
        'relations': [],
        'names': []
        }

    for rel in entity.inbound:
        rel_data = relations.to_index(rel)
        data['inbound'].append(rel_data)
        data['relations'].append(rel_data)

    for rel in entity.outbound:
        rel_data = relations.to_index(rel)
        data['outbound'].append(rel_data)
        data['relations'].append(rel_data)

    data['num_relations'] = entity.degree

    for prop in entity.properties:
        if prop.name == 'name':
            data['names'].append(prop.value)
        if prop.active:
            data[prop.name] = prop.value
            data['num_properties'] += 1

    return data


def to_rest_index(entity):
    """ Convert an entity to the REST API form. """
    props = {}
    for prop in entity.active_properties:
        name, prop = properties_logic.to_rest_index(prop)
        props[name] = prop
    return {
        'id': entity.id,
        'api_url': url_for('entities_api.view', id=entity.id),
        'properties': props
    }


def to_rest(entity):
    """ Full serialization of the entity. """
    data = to_rest_index(entity)
    data['created_at'] = entity.created_at
    data['updated_at'] = entity.updated_at

    ss = [schemata_logic.to_rest_index(s) for s in entity.schemata]
    data['schemata'] = ss
    return data
