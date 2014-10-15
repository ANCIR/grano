from flask import request
from sqlalchemy.orm import aliased

from grano.authz import permissions
from grano.model import Project, Relation
from grano.model import Entity, Property, Schema
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

        value = single_arg(key)
        q = cls._filter_property(q, prop, value, only_active=only_active)
    return q


def for_relations(q, Rel):
    #Source = aliased(Entity)
    #Target = aliased(Entity)
    #q = q.join(Source, Rel.source)
    #q = q.join(Target, Rel.target)

    q = q.filter(Rel.project_id.in_(permissions().get('reader')))

    project = single_arg('project')
    if project:
        Proj = aliased(Project)
        q = q.join(Proj, Rel.project)
        q = q.filter(Proj.slug == project)

    q = property_filters(Relation, q)

    if 'source' in request.args:
        q = q.filter(Rel.source_id == single_arg('source'))

    if 'target' in request.args:
        q = q.filter(Rel.target_id == single_arg('target'))

    schemata = request.args.getlist('schema')
    if len(schemata):
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
    q = q.filter(Ent.same_as == None) # noqa
    q = q.filter(Ent.project_id.in_(permissions().get('reader')))

    if 'project' in request.args:
        Proj = aliased(Project)
        q = q.join(Proj, Ent.project)
        q = q.filter(Proj.slug == single_arg('project'))

    q = property_filters(Entity, q)

    if 'q' in request.args and single_arg('q'):
        EntProp = aliased(Property)
        q_text = '%%%s%%' % single_arg('q')
        q = q.join(EntProp)
        q = q.filter(EntProp.name == 'name')
        q = q.filter(EntProp.value_string.ilike(q_text))

    schemata = request.args.getlist('schema')
    if len(schemata):
        alias = aliased(Schema)
        q = q.join(alias, Ent.schema)
        q = q.filter(alias.name.in_(schemata))

    return q
