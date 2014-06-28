from flask import request
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func

from grano.lib.exc import BadRequest
from grano.lib.pager import Pager
from grano.model import Project, Relation
from grano.model import Entity, EntityProperty, Schema, db
from grano.model import RelationProperty
from grano.views import filters


def apply_facet_obj(q, facet_obj):
    q = q.add_entity(facet_obj)
    return q.group_by(facet_obj)


def apply_property_facet(q, facet, cls, parent_obj):
    """ Property facets are complicated because we don't want
    to facet over the whole property object, but merely it's
    value - which can be in one of any number of fields. """
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


def parse_entity_facets(entity_obj, facet, q):
    """ Parse a facet related to a relation object and return a
    modified query. """
    # TODO: Status facet.
    if facet == 'project':
        facet_obj = aliased(Project)
        q = q.join(facet_obj, entity_obj.project)
        return apply_facet_obj(q, facet_obj)
    elif facet == 'schema':
        facet_obj = aliased(Schema)
        q = q.join(facet_obj, entity_obj.schemata)
        return apply_facet_obj(q, facet_obj)
    elif facet.startswith('properties.'):
        return apply_property_facet(q, facet, EntityProperty,
                                    entity_obj)
    elif facet.startswith('inbound.'):
        _, subfacet = facet.split('.', 1)
        rel_obj = aliased(Relation)
        q = q.join(rel_obj, entity_obj.inbound)
        return parse_relation_facets(rel_obj, subfacet, q)
    elif facet.startswith('outbound.'):
        _, subfacet = facet.split('.', 1)
        rel_obj = aliased(Relation)
        q = q.join(rel_obj, entity_obj.outbound)
        return parse_relation_facets(rel_obj, subfacet, q)
    else:
        raise BadRequest("Unknown facet: %s" % facet)


def parse_relation_facets(relation_obj, facet, q):
    """ Parse a facet related to an entity and return a modified
    query. """
    if facet == 'project':
        facet_obj = aliased(Project)
        q = q.join(facet_obj, relation_obj.project)
        return apply_facet_obj(q, facet_obj)
    elif facet == 'schema':
        facet_obj = aliased(Schema)
        q = q.join(facet_obj, relation_obj.schema)
        return apply_facet_obj(q, facet_obj)
    elif facet.startswith('properties.'):
        return apply_property_facet(q, facet, RelationProperty,
                                    relation_obj)
    elif facet.startswith('source.'):
        _, subfacet = facet.split('.', 1)
        ent_obj = aliased(Entity)
        q = q.join(ent_obj, relation_obj.source)
        return parse_entity_facets(ent_obj, subfacet, q)
    elif facet.startswith('target.'):
        _, subfacet = facet.split('.', 1)
        ent_obj = aliased(Entity)
        q = q.join(ent_obj, relation_obj.target)
        return parse_entity_facets(ent_obj, subfacet, q)
    else:
        raise BadRequest("Unknown facet: %s" % facet)


def results_process(q):
    for res in q:
        # pick the field that has a value, see the way properties
        # are queried. slight hack.
        count, value = res[0], max(res[1:])
        yield value, count


def for_entities():
    """ Return a set of facets based on the current query string. This
    will also consider filters set for the query, i.e. only show facets
    that match the current set of filters. """
    facets = {}
    for facet in request.args.getlist('facet'):
        entity_obj = aliased(Entity)
        q = db.session.query()
        facet_count = func.count(entity_obj.id)
        q = q.add_columns(facet_count)
        q = q.order_by(facet_count.desc())
        q = filters.for_entities(q, entity_obj)
        q = parse_entity_facets(entity_obj, facet, q)
        facets[facet] = Pager(q, name='facet_%s' % facet,
                              results_converter=results_process)
    return facets
