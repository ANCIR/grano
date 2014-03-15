from flask import Blueprint, render_template, request
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Relation, Schema
from grano.logic import relations
from grano.logic.references import ProjectRef
from grano.lib.pager import Pager
from grano.lib.exc import Gone
from grano.core import app, db
from grano.views.util import filter_query
from grano import authz


blueprint = Blueprint('relations_api', __name__)


@blueprint.route('/api/1/relations', methods=['GET'])
def index():
    query = filter_query(Relation, Relation.all(), request.args)

    if request.args.get('source'):
        query = query.filter(Relation.source_id==request.args.getlist('source')[0])

    if request.args.get('target'):
        query = query.filter(Relation.target_id==request.args.getlist('target')[0])
    
    if request.args.get('schema'):
        schemata = request.args.get('schema').split(',')
        query = query.join(Schema)
        query = query.filter(Schema.name.in_(schemata))

    pager = Pager(query)
    conv = lambda es: [relations.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))


@blueprint.route('/api/1/relations', methods=['POST', 'PUT'])
def create():
    data = request_data({'author': request.account})
    project = ProjectRef().get(data.get('project'))
    data['project'] = project
    authz.require(authz.project_edit(project))
    relation = relations.save(data)
    db.session.commit()
    return jsonify(relations.to_rest(relation))


@blueprint.route('/api/1/relations/<id>', methods=['GET'])
def view(id):
    relation = object_or_404(Relation.by_id(id))
    authz.require(authz.project_read(relation.project))
    return jsonify(relations.to_rest(relation))


@blueprint.route('/api/1/relations/<id>', methods=['POST', 'PUT'])
def update(id):
    relation = object_or_404(Relation.by_id(id))
    authz.require(authz.project_edit(relation.project))
    data = request_data({'author': request.account})
    relation = relations.save(data, relation=relation)
    db.session.commit()
    return jsonify(relations.to_rest(relation))


@blueprint.route('/api/1/relations/<id>', methods=['DELETE'])
def delete(id):
    relation = object_or_404(Relation.by_id(id))
    authz.require(authz.project_edit(relation.project))
    relations.delete(relation)
    db.session.commit()
    raise Gone()

