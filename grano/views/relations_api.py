from flask import Blueprint, request
from flask_pager import Pager
from sqlalchemy.orm import aliased

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Relation
from grano.logic import relations
from grano.logic.references import ProjectRef
from grano.views.cache import validate_cache
from grano.lib.exc import Gone
from grano.core import db
from grano.views import filters, facets
from grano import authz


blueprint = Blueprint('relations_api', __name__)


@blueprint.route('/api/1/relations', methods=['GET'])
def index():
    alias = aliased(Relation)
    q = db.session.query(alias)
    query = filters.for_relations(q, alias)
    pager = Pager(query)
    validate_cache(keys=pager.cache_keys())
    result = pager.to_dict()
    result['facets'] = facets.for_relations()
    return jsonify(result, index=True)


@blueprint.route('/api/1/relations', methods=['POST', 'PUT'])
def create():
    data = request_data({'author': request.account})
    project = ProjectRef().get(data.get('project'))
    data['project'] = project
    authz.require(authz.project_edit(project))
    relation = relations.save(data)
    db.session.commit()
    return jsonify(relation)


@blueprint.route('/api/1/relations/<id>', methods=['GET'])
def view(id):
    relation = object_or_404(Relation.by_id(id))
    authz.require(authz.relation_read(relation))
    return jsonify(relation)


@blueprint.route('/api/1/relations/<id>', methods=['POST', 'PUT'])
def update(id):
    relation = object_or_404(Relation.by_id(id))
    authz.require(authz.relation_edit(relation))
    data = request_data({'author': request.account})
    relation = relations.save(data, relation=relation)
    db.session.commit()
    return jsonify(relation)


@blueprint.route('/api/1/relations/<id>', methods=['DELETE'])
def delete(id):
    relation = object_or_404(Relation.by_id(id))
    authz.require(authz.relation_edit(relation))
    relations.delete(relation)
    db.session.commit()
    raise Gone()
