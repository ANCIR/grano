from flask import Blueprint, render_template, Response, request
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Project
from grano.logic import projects
from grano.lib.pager import Pager
from grano.logic.graph import GraphExtractor
from grano.lib.exc import Gone
from grano.core import app, db
from grano.views.cache import validate_cache
from grano import authz


blueprint = Blueprint('projects_api', __name__)


@blueprint.route('/api/1/projects', methods=['GET'])
def index():
    query = Project.all()
    pager = Pager(query)
    conv = lambda es: [projects.to_rest_index_stats(e) for e in es]
    return jsonify(pager.to_dict(conv))


@blueprint.route('/api/1/projects', methods=['POST', 'PUT'])
def create():
    authz.require(authz.project_create())
    project = projects.save(request_data({'author': request.account}))
    db.session.commit()
    return jsonify(projects.to_rest(project), status=201)


@blueprint.route('/api/1/projects/<slug>', methods=['GET'])
def view(slug):
    project = object_or_404(Project.by_slug(slug))
    validate_cache(last_modified=project.updated_at)
    return jsonify(projects.to_rest(project))


@blueprint.route('/api/1/projects/<slug>/graph', methods=['GET'])
def graph(slug):
    project = object_or_404(Project.by_slug(slug))
    extractor = GraphExtractor(project_id=project.id)
    validate_cache(keys=extractor.to_hash())
    if extractor.format == 'gexf':
        return Response(extractor.to_gexf(),
                mimetype='text/xml')
    return jsonify(extractor.to_dict())


@blueprint.route('/api/1/projects/<slug>', methods=['POST', 'PUT'])
def update(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    data = request_data({'author': request.account})
    project = projects.save(data, project=project)
    db.session.commit()
    return jsonify(projects.to_rest(project))


@blueprint.route('/api/1/projects/<slug>', methods=['DELETE'])
def delete(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_delete(project))
    projects.delete(project)
    db.session.commit()
    raise Gone()
