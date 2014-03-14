from flask import Blueprint, render_template, request, Response
from flask import redirect, make_response
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Entity, Schema, EntityProperty, Project, Permission
from grano.logic import entities, relations
from grano.logic.references import ProjectRef
from grano.logic.graph import GraphExtractor
from grano.logic.searcher import ESSearcher
from grano.lib.pager import Pager
from grano.lib.exc import Gone, BadRequest
from grano.core import app, db, url_for
from grano.views.util import filter_query
from grano.views.cache import validate_cache
from grano import authz


blueprint = Blueprint('entities_api', __name__)


@blueprint.route('/api/1/entities', methods=['GET'])
def index():
    query = filter_query(Entity, Entity.all(), request.args)

    for schema in request.args.getlist('schema'):
        alias = aliased(Schema)
        query = query.join(alias, Entity.schemata)
        query = query.filter(alias.name.in_(schema.split(',')))

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
    authz.require(authz.project_read(entity.project))
    return jsonify(entities.to_rest(entity))


@blueprint.route('/api/1/entities/_search', methods=['GET'])
def search():
    # TODO: move to be project-specific, the implement access control!
    searcher = ESSearcher(request.args)
    if 'project' in request.args:
        searcher.add_filter('project.slug', request.args.get('project'))
    pager = Pager(searcher)
    # TODO: get all entities at once:
    conv = lambda res: [entities.to_rest_index(Entity.by_id(r.get('id'))) for r in res]
    data = pager.to_dict(results_converter=conv)
    data['facets'] = searcher.facets()
    return jsonify(data)


@blueprint.route('/api/1/entities/_suggest', methods=['GET'])
def suggest():
    if not 'q' in request.args or not len(request.args.get('q').strip()):
        raise BadRequest("Missing the query ('q' parameter).")

    q = db.session.query(EntityProperty)
    q = q.join(Entity)
    q = q.join(Project)
    q = q.join(Permission)
    q = q.filter(or_(Project.private==False,
        and_(Permission.reader==True, Permission.account==request.account)))
        
    # TODO: authz check
    q = q.filter(EntityProperty.name=='name')
    q = q.filter(EntityProperty.active==True)
    q = q.filter(EntityProperty.entity_id!=None)
    q = q.filter(EntityProperty.value.ilike(request.args.get('q') + '%'))
    if 'project' in request.args:
        q = q.filter(Project.slug==request.args.get('project'))
    pager = Pager(q)

    data = []
    def convert(props):
        for prop in props:
            data.append({
                'name': prop.value,
                'api_url': url_for('entities_api.view', id=prop.entity_id)
            })
        return data

    validate_cache(keys='#'.join([d['name'] for d in data]))
    return jsonify(pager.to_dict(results_converter=convert))


@blueprint.route('/api/1/entities/<id>/graph', methods=['GET'])
def graph(id):
    entity = object_or_404(Entity.by_id(id))
    authz.require(authz.project_read(entity.project))
    extractor = GraphExtractor(root_id=entity.id)
    validate_cache(keys=extractor.to_hash())
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
