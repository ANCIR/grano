from flask import Blueprint, request
from sqlalchemy.orm import aliased

from grano.lib.serialisation import jsonify
from grano.lib.exc import BadRequest, Gone
from grano.lib.args import object_or_404, request_data
from grano.model import Entity, Property, Project
from grano.logic import entities
from grano.logic.references import ProjectRef
from grano.lib.pager import Pager
from grano.core import db, url_for
from grano.views import filters, facets
from grano.views.cache import validate_cache
from grano import authz


blueprint = Blueprint('entities_api', __name__)


@blueprint.route('/api/1/entities', methods=['GET'])
def index():
    alias = aliased(Entity)
    q = db.session.query(alias)
    query = filters.for_entities(q, alias)
    pager = Pager(query)
    validate_cache(keys=pager.cache_keys())
    result = pager.to_dict()
    result['facets'] = facets.for_entities()
    return jsonify(result, index=True)


@blueprint.route('/api/1/entities', methods=['POST', 'PUT'])
def create():
    data = request_data({'author': request.account})
    project = ProjectRef().get(data.get('project'))
    data['project'] = project
    authz.require(authz.project_edit(project))
    entity = entities.save(data, files=request.files)
    db.session.commit()
    return jsonify(entity)


@blueprint.route('/api/1/entities/<id>', methods=['GET'])
def view(id):
    entity = object_or_404(Entity.by_id(id))
    authz.require(authz.entity_read(entity))
    return jsonify(entity)


@blueprint.route('/api/1/entities/_suggest', methods=['GET'])
def suggest():
    if 'q' not in request.args or not len(request.args.get('q').strip()):
        raise BadRequest("Missing the query ('q' parameter).")

    q = db.session.query(Property)
    q = q.join(Entity)
    q = q.filter(Entity.project_id.in_(authz.permissions().get('reader')))
    q = q.filter(Property.name == 'name')
    q = q.filter(Property.active == True)
    q = q.filter(Property.entity_id != None)
    q = q.filter(Property.value_string.ilike(request.args.get('q') + '%'))
    if 'project' in request.args:
        q = q.filter(Project.slug == request.args.get('project'))
    q = q.distinct()
    pager = Pager(q)

    data = []

    def convert(props):
        for prop in props:
            data.append({
                'name': prop.value,
                'id': prop.entity_id,
                'api_url': url_for('entities_api.view', id=prop.entity_id)
            })
        return data

    validate_cache(keys='#'.join([d['name'] for d in data]))
    return jsonify(pager.to_dict(results_converter=convert))


@blueprint.route('/api/1/entities/<id>', methods=['POST', 'PUT'])
def update(id):
    entity = object_or_404(Entity.by_id(id))
    authz.require(authz.entity_edit(entity))
    data = request_data({'author': request.account})
    entity = entities.save(data, files=request.files, entity=entity)
    db.session.commit()
    return jsonify(entity)


@blueprint.route('/api/1/entities/_merge', methods=['POST', 'PUT'])
def merge():
    validator = entities.MergeValidator()
    data = validator.deserialize(request_data())
    authz.require(authz.project_edit(data['orig'].project))

    if data['orig'].id == data['dest'].id:
        raise BadRequest('Origin and destination are identical.')

    if data['orig'].project_id != data['dest'].project_id:
        raise BadRequest('Entities belong to different projects.')

    dest = entities.merge(data['orig'], data['dest'])
    db.session.commit()
    return jsonify(dest)


@blueprint.route('/api/1/entities/<id>', methods=['DELETE'])
def delete(id):
    entity = object_or_404(Entity.by_id(id))
    authz.require(authz.entity_edit(entity))
    entities.delete(entity)
    db.session.commit()
    raise Gone()
