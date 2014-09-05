from StringIO import StringIO

from flask import Blueprint, request
from flask import send_file
from flask_pager import Pager

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Project
from grano.logic import projects
from grano.logic.aliases import export_aliases
from grano.lib.exc import Gone
from grano.core import db
from grano.views.cache import validate_cache
from grano import authz


blueprint = Blueprint('projects_api', __name__)


@blueprint.route('/api/1/projects', methods=['GET'])
def index():
    q = Project.all()
    q = q.filter(Project.id.in_(authz.permissions().get('reader')))
    pager = Pager(q)
    validate_cache(keys=pager.cache_keys())
    return jsonify(pager, index=True)


@blueprint.route('/api/1/projects', methods=['POST', 'PUT'])
def create():
    authz.require(authz.project_create())
    project = projects.save(request_data({'author': request.account}))
    db.session.commit()
    return jsonify(project, status=201)


@blueprint.route('/api/1/projects/<slug>', methods=['GET'])
def view(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_read(project))
    if not project.private:
        validate_cache(last_modified=project.updated_at)
    return jsonify(project)


@blueprint.route('/api/1/projects/<slug>/aliases', methods=['GET'])
def aliases(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_read(project))
    sio = StringIO()
    export_aliases(project, sio)
    sio.seek(0)
    res = send_file(sio, mimetype='text/csv')
    res.headers['Content-Disposition'] = 'filename=%s-aliases.csv' % project.slug
    return res


@blueprint.route('/api/1/projects/<slug>', methods=['POST', 'PUT'])
def update(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    data = request_data({'author': request.account})
    project = projects.save(data, project=project)
    db.session.commit()
    return jsonify(project)


@blueprint.route('/api/1/projects/<slug>', methods=['DELETE'])
def delete(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_delete(project))
    projects.delete(project)
    db.session.commit()
    raise Gone()


@blueprint.route('/api/1/projects/<slug>/_truncate', methods=['DELETE'])
def truncate(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_delete(project))
    projects.truncate(project)
    db.session.commit()
    return jsonify(project)
