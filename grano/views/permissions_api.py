from flask import Blueprint, render_template, request
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Permission, Project
from grano.views.cache import validate_cache
from grano.logic import permissions
from grano.lib.pager import Pager
from grano.lib.exc import Gone
from grano.core import app, db
from grano import authz


blueprint = Blueprint('permissions_api', __name__)


@blueprint.route('/api/1/projects/<slug>/permissions', methods=['GET'])
def index(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    query = Permission.all()
    query = query.filter_by(project=project)
    pager = Pager(query, slug=slug)
    validate_cache(keys=pager.cache_keys())
    conv = lambda es: [permissions.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))


@blueprint.route('/api/1/projects/<slug>/permissions', methods=['POST', 'PUT'])
def create(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    data = request_data({'project': project})
    permission = permissions.save(data)
    db.session.commit()
    return jsonify(permissions.to_rest(permission), status=201)


@blueprint.route('/api/1/projects/<slug>/permissions/<id>', methods=['GET'])
def view(slug, id):
    project = object_or_404(Project.by_slug(slug))
    permission = object_or_404(Permission.by_project_and_id(project, id))
    authz.require(authz.project_manage(project) or request.account==permission.account)
    return jsonify(permissions.to_rest(permission))


@blueprint.route('/api/1/projects/<slug>/permissions/<id>', methods=['POST', 'PUT'])
def update(slug, id):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    permission = object_or_404(Permission.by_project_and_id(project, id))
    data = request_data({'project': project})
    permission = permissions.save(data, permission=permission)
    db.session.commit()
    return jsonify(permissions.to_rest(permission))


@blueprint.route('/api/1/projects/<slug>/permissions/<id>', methods=['DELETE'])
def delete(slug, id):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    permission = object_or_404(Permission.by_project_and_id(project, id))
    permissions.delete(permission)
    db.session.commit()
    raise Gone()
