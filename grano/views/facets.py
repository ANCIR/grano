from flask import request
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func

from grano.lib.exc import BadRequest
from grano.model import Project, Relation
from grano.model import Entity, EntityProperty, Schema, db
from grano.model import RelationProperty
from grano.views import filters


def entity_facet_obj(entity_obj, facet, q):
    if facet == 'project':
        facet_obj = aliased(Project)
        q = q.join(facet_obj, entity_obj.project)
    elif facet == 'schema':
        facet_obj = aliased(Schema)
        q = q.join(facet_obj, entity_obj.schemata)
    elif facet.startswith('properties.'):
        _, name = facet.split('.', 1)
        facet_obj = aliased(EntityProperty)
        q = q.join(facet_obj, entity_obj.properties)
        q = q.filter(facet_obj.active == True)
        q = q.filter(facet_obj.name == name)
    elif facet.startswith('inbound.'):
        _, subfacet = facet.split('.', 1)
        rel_obj = aliased(Relation)
        q = q.join(rel_obj, entity_obj.inbound)
        return relation_facet_obj(rel_obj, subfacet, q)
    elif facet.startswith('outbound.'):
        _, subfacet = facet.split('.', 1)
        rel_obj = aliased(Relation)
        q = q.join(rel_obj, entity_obj.outbound)
        return relation_facet_obj(rel_obj, subfacet, q)
    else:
        raise BadRequest("Unknown facet: %s" % facet)
    return q, facet_obj


def relation_facet_obj(relation_obj, facet, q):
    if facet == 'project':
        facet_obj = aliased(Project)
        q = q.join(facet_obj, relation_obj.project)
    elif facet == 'schema':
        facet_obj = aliased(Schema)
        q = q.join(facet_obj, relation_obj.schema)
    elif facet.startswith('properties.'):
        _, name = facet.split('.', 1)
        facet_obj = aliased(RelationProperty)
        q = q.join(facet_obj, relation_obj.properties)
        q = q.filter(facet_obj.active == True)
        q = q.filter(facet_obj.name == name)
    elif facet.startswith('source.'):
        _, subfacet = facet.split('.', 1)
        ent_obj = aliased(Entity)
        q = q.join(ent_obj, relation_obj.source)
        return entity_facet_obj(ent_obj, subfacet, q)
    elif facet.startswith('target.'):
        _, subfacet = facet.split('.', 1)
        ent_obj = aliased(Entity)
        q = q.join(ent_obj, relation_obj.target)
        return entity_facet_obj(ent_obj, subfacet, q)
    else:
        raise BadRequest("Unknown facet: %s" % facet)
    return q, facet_obj


def for_entities():
    facets = {}
    for facet in request.args.getlist('facet'):
        entity_obj = aliased(Entity)
        q = db.session.query()
        q, facet_obj = entity_facet_obj(entity_obj, facet, q)
        facet_count = func.count(entity_obj.id)
        q = q.add_entity(facet_obj)
        q = q.add_columns(facet_count)
        q = filters.for_entities(q, entity_obj)
        q = q.order_by(facet_count.desc())
        q = q.group_by(facet_obj)
        facets[facet] = q.all()
    return facets

