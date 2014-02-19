from flask import Blueprint, render_template, request, Response
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Entity
from grano.logic import entities, relations
from grano.logic.references import ProjectRef
from grano.logic.graph import GraphExtractor
from grano.lib.pager import Pager
from grano.lib.exc import Gone
from grano.core import app, db
from grano.views.util import filter_query
from grano import authz


blueprint = Blueprint('entities_api', __name__)


@blueprint.route('/api/1/entities', methods=['GET'])
def index():
    query = filter_query(Entity, Entity.all(), request.args)
    pager = Pager(query)
    conv = lambda es: [entities.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))


@blueprint.route('/api/1/entities', methods=['POST', 'PUT'])
def create():
    data = request_data({'author': request.account})
    project = ProjectRef().get(data.get('project'))
    data['project'] = project
    authz.require(authz.project_edit(project))
    entity = entities.save(data)
    db.session.commit()
    return jsonify(entities.to_rest(entity))


@blueprint.route('/api/1/entities/<id>', methods=['GET'])
def view(id):
    entity = object_or_404(Entity.by_id(id))
    return jsonify(entities.to_rest(entity))


@blueprint.route('/api/1/entities/<id>/graph', methods=['GET'])
def graph(id):
    entity = object_or_404(Entity.by_id(id))
    extractor = GraphExtractor(root_id=entity.id)
    if extractor.format == 'gexf':
        return Response(extractor.to_gexf(),
                mimetype='text/xml')
    return jsonify(extractor.to_dict())


@blueprint.route('/api/1/entities/<id>', methods=['POST', 'PUT'])
def update(id):
    entity = object_or_404(Entity.by_id(id))
    authz.require(authz.project_edit(entity.project))
    data = request_data({'author': request.account})
    entity = entities.save(data, entity=entity)
    db.session.commit()
    return jsonify(entities.to_rest(entity))


@blueprint.route('/api/1/entities/<id>', methods=['DELETE'])
def delete(id):
    entity = object_or_404(Entity.by_id(id))
    authz.require(authz.project_edit(entity.project))
    entities.delete(entity)
    db.session.commit()
    raise Gone()
