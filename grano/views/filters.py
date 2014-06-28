from flask import request
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased

from grano.model import Project, Permission, Attribute, Relation
from grano.model import Entity, EntityProperty, Schema
from grano.authz import PUBLISHED_THRESHOLD
from grano.lib.args import single_arg


PROPERTY = 'property-'
ALIASES = 'aliases-'


def property_filters(cls, q):
    """ Parse the query arguments and apply any specified property
    filters to the given query ``q``. The property-holding object
    (a relation or entity) is given as ``cls``. """
    for key in request.args.keys():
        if not key.startswith(PROPERTY):
            continue
        prop = key[len(PROPERTY):]

        only_active = True
        if prop.startswith(ALIASES):
            prop = prop[len(ALIASES):]
            only_active = False

        attributes = Attribute.all_named(prop)
        value = single_arg(key)
        q = cls._filter_property(q, attributes, value,
                                 only_active=only_active)
    return q


def for_relations(q, Rel):
    Proj = aliased(Project)
    Perm = aliased(Permission)
    q = q.join(Proj, Rel.project)
    q = q.outerjoin(Perm, Proj.permissions)

    # TODO: Entity status checks
    q = q.filter(or_(Proj.private == False,
                 and_(Perm.reader == True, Perm.account == request.account)))

    project = single_arg('project')
    if project:
        q = q.filter(Proj.slug == project)

    q = property_filters(Relation, q)

    if 'source' in request.args:
        q = q.filter(Rel.source_id == single_arg('source'))

    if 'target' in request.args:
        q = q.filter(Rel.target_id == single_arg('target'))

    if 'schema' in request.args:
        schemata = request.args.get('schema').split(',')
        alias = aliased(Schema)
        q = q.join(alias, Rel.schema)
        q = q.filter(alias.name.in_(schemata))

    return q


def for_entities(q, Ent):
    """ Get all entities the current user has access to. Accepts project and
    additional filter parameters. """
    # NOTE: I'm passing in the query and entity alias so that this
    # function can be re-used from the facetting code to constrain
    # the results of the facet sub-query.
    Proj = aliased(Project)
    Perm = aliased(Permission)
    q = q.join(Proj, Ent.project).outerjoin(Perm, Proj.permissions)
    q = q.filter(Ent.same_as == None)

    q = q.filter(or_(
        and_(
            Proj.private == False,
            Ent.status >= PUBLISHED_THRESHOLD,
        ),
        and_(
            Perm.reader == True,
            Ent.status >= PUBLISHED_THRESHOLD,
            Perm.account == request.account
        ),
        and_(
            Perm.editor == True,
            Perm.account == request.account
        )
    ))

    if 'project' in request.args:
        q = q.filter(Proj.slug == single_arg('project'))

    q = property_filters(Entity, q)

    if 'q' in request.args and single_arg('q'):
        EntProp = aliased(EntityProperty)
        q_text = '%%%s%%' % single_arg('q')
        q = q.join(EntProp)
        q = q.filter(EntProp.name == 'name')
        q = q.filter(EntProp.value_string.ilike(q_text))

    for schema in request.args.getlist('schema'):
        if not len(schema.strip()):
            continue
        alias = aliased(Schema)
        q = q.join(alias, Ent.schemata)
        q = q.filter(alias.name.in_(schema.split(',')))

    return q
