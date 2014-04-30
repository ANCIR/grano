from flask import request
from sqlalchemy import or_, and_

from grano.model import Project, Permission, Attribute


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

        yield prop, args.get(key), only_active



def filter_query(cls, q, args):
    q = q.join(Project)
    q = q.outerjoin(Permission)
    q = q.filter(or_(Project.private==False,
        and_(Permission.reader==True, Permission.account==request.account)))
    
    project = args.get('project')
    if project:
        q = q.filter(Project.slug==project)
    
    for prop, value, only_active in property_filters(args):
        attributes = Attribute.all_named(prop)
        q = cls._filter_property(q, attributes, value,
                only_active=only_active)

    q = q.distinct()
    return q
