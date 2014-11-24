import logging
import colander

from grano.core import db, celery
from grano.model import Entity
from grano.lib.exc import Conflict
from grano.logic import properties as properties_logic
from grano.logic.references import ProjectRef, AccountRef
from grano.logic.references import SchemaRef, EntityRef
from grano.logic.validation import validate_saveoptions
from grano.plugins import notify_plugins


log = logging.getLogger(__name__)


class EntityBaseValidator(colander.MappingSchema):
    author = colander.SchemaNode(AccountRef())
    project = colander.SchemaNode(ProjectRef())


class MergeValidator(colander.MappingSchema):
    orig = colander.SchemaNode(EntityRef())
    dest = colander.SchemaNode(EntityRef())


def validate(data, entity):
    """ Due to some fairly weird interdependencies between the different
    elements of the model, validation of entities has to happen in three
    steps. """
    validator = EntityBaseValidator()
    sane = validator.deserialize(data)
    project = sane.get('project')

    schema_validator = colander.SchemaNode(colander.Mapping())
    schema_validator.add(colander.SchemaNode(SchemaRef(project),
                         name='schema'))
    sane.update(schema_validator.deserialize(data))

    sane['properties'] = properties_logic.validate('entity', entity,
                                                   project, sane.get('schema'),
                                                   data.get('properties', []))
    return sane


@celery.task
def _entity_changed(entity_id, operation):
    """ Notify plugins about changes to an entity. """
    def _handle(obj):
        obj.entity_changed(entity_id, operation)
    notify_plugins('grano.entity.change', _handle)


def save(data, files=None, entity=None, options=None):
    """ Save or update an entity. """
    options = validate_saveoptions(options)
    data = validate(data, entity)

    operation = 'create' if entity is None else 'update'
    deactivate_props = True
    if entity is None:
        entity = Entity.by_unique_properties(
            project=data.get('project'),
            schema=data.get('schema'),
            properties=data.get('properties')
        ).first()
        if entity is None:
            entity = Entity()
            entity.project = data.get('project')
            entity.author = data.get('author')
            db.session.add(entity)
        else:
            conflict_action = options.get('onconflict')
            operation = 'update'
            if conflict_action == 'merge':
                deactivate_props = False
            elif conflict_action == 'error':
                raise Conflict("Entity with unique properties already exists")

    entity.schema = data.get('schema')

    prop_names = set()
    for name, prop in data.get('properties').items():
        prop_names.add(name)
        prop['project'] = entity.project
        prop['name'] = name
        prop['author'] = data.get('author')
        properties_logic.save(entity, prop, files=files)

    if deactivate_props:
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


def merge(source, dest):
    """ Copy all properties and relations from one entity onto another, then
    mark the source entity as an ID alias for the destionation entity. """
    if source.id == dest.id:
        return source

    if dest.same_as == source.id:
        return source

    if source.same_as == dest.id:
        return dest

    if dest.same_as is not None:
        # potential infinite recursion here.
        canonical = Entity.by_id(dest.same_as)
        if canonical is not None:
            return merge(source, canonical)

    source_schema = source.schema
    if dest.schema.is_parent(source_schema):
        dest.schema = source_schema
    else:
        source_schema = dest.schema.common_parent(source_schema)

    source_valid = [a.name for a in source_schema.attributes]
    dest_active = [p.name for p in dest.active_properties]
    for prop in source.properties:
        if prop.name in source_valid:
            if prop.name in dest_active:
                prop.active = False
            prop.entity = dest
        else:
            properties_logic.delete(prop)

    for rel in source.inbound:
        rel.target = dest

    for rel in source.outbound:
        rel.source = dest

    source.same_as = dest.id
    db.session.flush()
    _entity_changed.delay(dest.id, 'update')
    _entity_changed.delay(source.id, 'delete')
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
            if prop.value == canonical_name:
                prop.active = True
            else:
                prop.active = False

        if canonical is not None and canonical.id != existing.id:
            canonical = merge(existing, canonical)
        else:
            canonical = existing

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
