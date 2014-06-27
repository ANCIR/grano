from flask import Blueprint, request
from sqlalchemy.orm import aliased

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Relation
from grano.logic import relations
from grano.logic.references import ProjectRef
from grano.views.cache import validate_cache
from grano.lib.pager import Pager
from grano.lib.exc import Gone
from grano.core import db
from grano.views.util import relations_query
from grano import authz


blueprint = Blueprint('relations_api', __name__)


@blueprint.route('/api/1/relations', methods=['GET'])
def index():
    alias = aliased(Relation)
    q = db.session.query(alias)
    query = relations_query(q, alias)
    query = query.distinct()
    pager = Pager(query)
    validate_cache(keys=pager.cache_keys())
    return jsonify(pager, index=True)


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
    authz.require(authz.project_read(relation.project))
    return jsonify(relation)


@blueprint.route('/api/1/relations/<id>', methods=['POST', 'PUT'])
def update(id):
    relation = object_or_404(Relation.by_id(id))
    authz.require(authz.project_edit(relation.project))
    data = request_data({'author': request.account})
    relation = relations.save(data, relation=relation)
    db.session.commit()
    return jsonify(relation)


@blueprint.route('/api/1/relations/<id>', methods=['DELETE'])
def delete(id):
    relation = object_or_404(Relation.by_id(id))
    authz.require(authz.project_edit(relation.project))
    relations.delete(relation)
    db.session.commit()
    raise Gone()

