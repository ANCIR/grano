from flask import request
from sqlalchemy import or_, and_

from grano.model import Project, Permission, Attribute, Entity
from grano.authz import PUBLISHED_THRESHOLD
from grano.lib.args import single_arg


PROPERTY = 'property-'
ALIASES = 'aliases-'


def property_filters(args):
    for key in args.keys():
        if not key.startswith(PROPERTY):
            continue
        prop = key[len(PROPERTY):]

        only_active = True
        if prop.startswith(ALIASES):
            prop = prop[len(ALIASES):]
            only_active = False

        yield prop, single_arg(args, key), only_active



def filter_query(cls, q, args):
    q = q.join(Project)
    q = q.outerjoin(Permission)
    q = q.filter(or_(Project.private==False,
        and_(Permission.reader==True, Permission.account==request.account)))
    
    project = single_arg(args, 'project')
    if project:
        q = q.filter(Project.slug==project)
    
    for prop, value, only_active in property_filters(args):
        attributes = Attribute.all_named(prop)
        q = cls._filter_property(q, attributes, value,
                only_active=only_active)

    q = q.distinct()
    return q


def all_entities(args=None):
    """Get all entities the current user has access to. Accepts project and
    additional filter parameters."""
    if args is None:
        args = request.args
    q = Entity.all().\
        join(Project).\
        outerjoin(Permission)
    q = q.filter(Entity.same_as==None)
    q = q.filter(or_(
        and_(
            Project.private==False,
            Entity.status>=PUBLISHED_THRESHOLD,
        ),
        and_(
            Permission.reader==True,
            Entity.status>=PUBLISHED_THRESHOLD,
            Permission.account==request.account
        ),
        and_(
            Permission.editor==True,
            Permission.account==request.account
        )
    ))
    if 'project' in args:
        q = q.filter(Project.slug==single_arg(args, 'project'))
    for prop, value, only_active in property_filters(args):
        attributes = Attribute.all_named(prop)
        q = Entity._filter_property(q, attributes, value,
                only_active=only_active)
    q = q.distinct()
    return q
