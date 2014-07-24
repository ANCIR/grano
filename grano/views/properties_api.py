from flask import Blueprint, request

from grano.lib.serialisation import jsonify
from grano.model import Property, Relation, Entity
from grano.views.cache import validate_cache
from grano.lib.pager import Pager
from grano.lib.args import arg_bool
from grano import authz


blueprint = Blueprint('properties_api', __name__)


@blueprint.route('/api/1/relations/<obj_id>/properties', methods=['GET'])
def relations_index(obj_id):
    query = Property.all()
    query = query.filter(Property.relation_id != None)
    obj = Relation.by_id(obj_id)
    query = query.filter_by(relation_id=obj_id)
    return _index(query, obj)


@blueprint.route('/api/1/entities/<obj_id>/properties', methods=['GET'])
def entities_index(obj_id):
    query = Property.all()
    query = query.filter(Property.relation_id != None)
    obj = Entity.by_id(obj_id)
    query = query.filter_by(entity_id=obj_id)
    return _index(query, obj)


def _index(query, obj):
    authz.require(authz.project_read(obj.project))
    active_only = arg_bool('active', default=True)
    if active_only:
        query = query.filter_by(active=True)

    if 'name' in request.args:
        query = query.filter_by(name=request.args.get('name'))

    query = query.order_by(Property.created_at.desc())
    pager = Pager(query, obj_id=obj.id)
    validate_cache(keys=pager.cache_keys())
    return jsonify(pager, index=False)
