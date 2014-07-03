import logging
import colander

from grano.core import db, celery
from grano.model import Entity, Schema
from grano.logic import properties as properties_logic
from grano.logic.references import ProjectRef, AccountRef
from grano.logic.references import SchemaRef, EntityRef
from grano.plugins import notify_plugins


log = logging.getLogger(__name__)


class EntityBaseValidator(colander.MappingSchema):
    author = colander.SchemaNode(AccountRef())
    project = colander.SchemaNode(ProjectRef())
    status = colander.SchemaNode(colander.Integer(),
                                 default=20,
                                 missing=20,
                                 validator=colander.Range(0, 100))


class MergeValidator(colander.MappingSchema):
    orig = colander.SchemaNode(EntityRef())
    dest = colander.SchemaNode(EntityRef())


def validate(data, entity):
    """ Due to some fairly weird interdependencies between the different
    elements of the model, validation of entities has to happen in three
    steps. """

    # a bit hacky
    data['schemata'] = data.get('schemata', []) + ['base']

    validator = EntityBaseValidator()
    sane = validator.deserialize(data)

    schemata_validator = colander.SchemaNode(colander.Mapping())
    schemata_node = colander.SchemaNode(SchemaRef(sane.get('project')))
    schemata_validator.add(colander.SchemaNode(colander.Sequence(),
                           schemata_node, name='schemata'))

    sane['schemata'] = []
    ids = set()
    for schema in schemata_validator.deserialize(data).get('schemata'):
        if schema is None or schema.id in ids:
            continue
        ids.add(schema.id)
        sane['schemata'].append(schema)

    sane['properties'] = properties_logic.validate(
        'entity', entity, sane['schemata'], sane.get('project'),
        data.get('properties', []))
    return sane


@celery.task
def _entity_changed(entity_id, operation):
    """ Notify plugins about changes to an entity. """
    def _handle(obj):
        obj.entity_changed(entity_id, operation)
    notify_plugins('grano.entity.change', _handle)


def save(data, entity=None):
    """ Save or update an entity. """
    data = validate(data, entity)

    operation = 'create' if entity is None else 'update'
    if entity is None:
        entity = Entity()
        entity.project = data.get('project')
        entity.author = data.get('author')
        db.session.add(entity)

    entity.status = data.get('status')
    entity.schemata = data.get('schemata')

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
    _entity_changed.delay(entity.id, operation)
    return entity


def delete(entity):
    """ Delete the entity and its properties, as well as any associated
    relations. """
    db.session.delete(entity)
    _entity_changed.delay(entity.id, 'delete')


def merge(orig, dest):
    """ Copy all properties and relations from one entity onto another, then
    mark the source entity as an ID alias for the destionation entity. """
    if orig.id == dest.id:
        return orig

    if dest.same_as == orig.id:
        return orig

    if orig.same_as == dest.id:
        return dest

    if dest.same_as is not None:
        # potential infinite recursion here.
        resolved_dest = Entity.by_id(dest.same_as)
        if resolved_dest is not None:
            return merge(orig, resolved_dest)

    schemata, seen_schemata = list(), set()
    for schema in dest.schemata + orig.schemata:
        if schema.id in seen_schemata:
            continue
        seen_schemata.add(schema.id)
        schemata.append(schema)

    dest.schemata = schemata

    dest_active = [p.name for p in dest.active_properties]
    for prop in orig.properties:
        if prop.name in dest_active:
            prop.active = False
        prop.entity = dest

    for rel in orig.inbound:
        rel.target = dest

    for rel in orig.outbound:
        rel.source = dest

    orig.same_as = dest.id
    dest.same_as = None
    db.session.flush()
    _entity_changed.delay(dest.id, 'update')
    _entity_changed.delay(orig.id, 'delete')
    return dest


def apply_alias(project, author, canonical_name, alias_name, source_url=None):
    """ Given two names, find out if there are existing entities for one or
    both of them. If so, merge them into a single entity - or, if only the
    entity associated with the alias exists - re-name the entity. """

    # Don't import meaningless aliases.
    if not len(canonical_name) or not len(alias_name):
        return log.info("Not an alias: %s", canonical_name)

    canonical = None

    # de-duplicate existing entities with the same name.
    known_names = set()
    for existing in Entity.by_name_many(project, canonical_name):

        for prop in existing.properties:
            if prop.name != 'name':
                continue
            known_names.add(prop.value)

            # make sure the canonical name is actually active
            # TODO: is this desirable?
            if prop.value == canonical_name:
                prop.active = True
            else:
                prop.active = False

        if canonical is not None and canonical.id != existing.id:
            canonical = merge(existing, canonical)
        else:
            canonical = existing

    schema = Schema.by_name(project, 'base')
    attribute = schema.get_attribute('name')

    # Find aliases, i.e. entities with the alias name which are not
    # the canonical entity.
    q = Entity.by_name_many(project, alias_name)
    if canonical is not None:
        q = q.filter(Entity.id != canonical.id)
    aliases = q.all()

    # If there are no existing aliases with that name, add the alias
    # name to the canonical entity.
    if not len(aliases) and canonical is not None:
        if alias_name not in known_names:
            data = {
                'value': alias_name,
                'schema': schema,
                'attribute': attribute,
                'active': False,
                'name': 'name',
                'source_url': source_url
            }
            properties_logic.save(canonical, data)
            _entity_changed.delay(canonical.id, 'update')
        log.info("Alias: %s -> %s", alias_name, canonical_name)

    for alias in aliases:
        if canonical is None:
            # Rename an alias to its new, canonical name.
            data = {
                'value': canonical_name,
                'schema': schema,
                'attribute': attribute,
                'active': True,
                'name': 'name',
                'source_url': source_url
            }
            properties_logic.save(alias, data)
            _entity_changed.delay(alias.id, 'update')
            log.info("Renamed: %s -> %s", alias_name, canonical_name)
        else:
            # Merge two existing entities, declare one as "same_as"
            merge(alias, canonical)
            log.info("Mapped: %s -> %s", alias.id, canonical.id)

    db.session.commit()
