from flask import request
from sqlalchemy import or_, and_

from grano.model import Project, Permission, Attribute, Entity
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



def filter_query(cls, q, args):
    q = q.join(Project)
    q = q.outerjoin(Permission)
    q = q.filter(or_(Project.private==False,
        and_(Permission.reader==True, Permission.account==request.account)))

    project = single_arg(args, 'project')
    if project:
        q = q.filter(Project.slug==project)

    q = property_filters(cls, q)

    q = q.distinct()
    return q


def all_entities():
    """Get all entities the current user has access to. Accepts project and
    additional filter parameters."""
    q = Entity.all().\
        join(Project).\
        outerjoin(Permission)
    q = q.filter(Entity.same_as == None)
    q = q.filter(or_(
        and_(
            Project.private == False,
            Entity.status >= PUBLISHED_THRESHOLD,
        ),
        and_(
            Permission.reader == True,
            Entity.status >= PUBLISHED_THRESHOLD,
            Permission.account == request.account
        ),
        and_(
            Permission.editor == True,
            Permission.account == request.account
        )
    ))
    if 'project' in request.args:
        q = q.filter(Project.slug == single_arg('project'))

    q = property_filters(Entity, q)
    return q


def generate_facets(args):
    facets = {}
    for facet in args.getlist('facet'):
        facets[facet] = facet_by(facet)
    return facets

from grano.model import Schema, db
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func

def facet_by(field):
    facet_obj = aliased(Schema)
    entity_obj = aliased(Entity)
    q = db.session.query(facet_obj)
    q = q.join(entity_obj, facet_obj.entities)
    facet_count = func.count(entity_obj.id)
    q = q.add_columns(facet_count)
    q = q.order_by(facet_count.desc())
    q = q.group_by(facet_obj)
    print q
    return q.all()


