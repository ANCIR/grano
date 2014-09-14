from flask import request
from restpager import Pager
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func

from grano.lib.exc import BadRequest
from grano.lib.args import arg_bool
from grano.model import Project, Relation
from grano.model import Entity, Property, Schema, db
from grano.views import filters


def apply_facet_obj(q, facet_obj):
    q = q.add_entity(facet_obj)
    return q.group_by(facet_obj)


def apply_property_facet(q, facet, cls, parent_obj):
    """ Property facets are complicated because we don't want
    to facet over the whole property object, but merely it's
    value - which can be in one of any number of fields. """
    if '.' not in facet:
        raise BadRequest("Invalud facet: %s" % facet)
    _, name = facet.split('.', 1)
    facet_obj = aliased(cls)
    q = q.join(facet_obj, parent_obj.properties)
    q = q.filter(facet_obj.active == True)
    q = q.filter(facet_obj.name == name)
    columns = (facet_obj.value_string, facet_obj.value_integer,
               facet_obj.value_float, facet_obj.value_datetime,
               facet_obj.value_boolean)
    q = q.add_columns(*columns)
    return q.group_by(*columns)


def parse_entity_facets(entity_obj, full_facet, facet, q):
    """ Parse a facet related to a relation object and return a
    modified query. """
    # TODO: Status facet.
    # TODO: Author facet.
    if facet == 'project':
        facet_obj = aliased(Project)
        q = q.join(facet_obj, entity_obj.project)
        return apply_facet_obj(q, facet_obj)
    elif facet == 'schema':
        facet_obj = aliased(Schema)
        if not arg_bool('facet_%s_hidden' % full_facet, default=False):
            q = q.filter(facet_obj.hidden == False)
        q = q.join(facet_obj, entity_obj.schema)
        return apply_facet_obj(q, facet_obj)
    elif facet.startswith('properties.'):
        return apply_property_facet(q, facet, Property,
                                    entity_obj)
    elif facet.startswith('inbound.'):
        _, subfacet = facet.split('.', 1)
        rel_obj = aliased(Relation)
        q = q.join(rel_obj, entity_obj.inbound)
        return parse_relation_facets(rel_obj, full_facet, subfacet, q)
    elif facet.startswith('outbound.'):
        _, subfacet = facet.split('.', 1)
        rel_obj = aliased(Relation)
        q = q.join(rel_obj, entity_obj.outbound)
        return parse_relation_facets(rel_obj, full_facet, subfacet, q)
    else:
        raise BadRequest("Unknown facet: %s" % facet)


def parse_relation_facets(relation_obj, full_facet, facet, q):
    """ Parse a facet related to an entity and return a modified
    query. """
    if facet == 'project':
        facet_obj = aliased(Project)
        q = q.join(facet_obj, relation_obj.project)
        return apply_facet_obj(q, facet_obj)
    elif facet == 'schema':
        facet_obj = aliased(Schema)
        if not arg_bool('facet_%s_hidden' % full_facet, default=False):
            q = q.filter(facet_obj.hidden == False)
        q = q.join(facet_obj, relation_obj.schema)
        return apply_facet_obj(q, facet_obj)
    elif facet.startswith('properties.'):
        return apply_property_facet(q, facet, Property,
                                    relation_obj)
    elif facet.startswith('source.'):
        _, subfacet = facet.split('.', 1)
        ent_obj = aliased(Entity)
        q = q.join(ent_obj, relation_obj.source)
        return parse_entity_facets(ent_obj, full_facet, subfacet, q)
    elif facet.startswith('target.'):
        _, subfacet = facet.split('.', 1)
        ent_obj = aliased(Entity)
        q = q.join(ent_obj, relation_obj.target)
        return parse_entity_facets(ent_obj, full_facet, subfacet, q)
    else:
        raise BadRequest("Unknown facet: %s" % facet)


def results_process(q):
    for res in q:
        # pick the field that has a value, see the way properties
        # are queried. slight hack.
        count, value = res[0], max(res[1:])
        yield value, count


def for_entities():
    return make_facets(lambda: aliased(Entity),
                       filters.for_entities,
                       parse_entity_facets)


def for_relations():
    return make_facets(lambda: aliased(Relation),
                       filters.for_relations,
                       parse_relation_facets)


def make_facets(parent_alias, filter_func, parser_func):
    """ Return a set of facets based on the current query string. This
    will also consider filters set for the query, i.e. only show facets
    that match the current set of filters. """
    facets = {}
    for facet in request.args.getlist('facet'):
        parent_obj = parent_alias()
        q = db.session.query()
        facet_count = func.count(parent_obj.id)
        q = q.add_columns(facet_count)
        q = q.order_by(facet_count.desc())
        q = filter_func(q, parent_obj)
        q = parser_func(parent_obj, facet, facet, q)
        facets[facet] = Pager(q, name='facet_%s' % facet,
                              results_converter=results_process)
    return facets
