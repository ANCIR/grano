from flask import Blueprint
from restpager import Pager

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data, arg_bool
from grano.model import Schema, Project
from grano.logic import schemata
from grano.lib.exc import Gone
from grano.core import db
from grano.views.cache import validate_cache
from grano import authz


blueprint = Blueprint('schemata_api', __name__)


@blueprint.route('/api/1/projects/<slug>/schemata', methods=['GET'])
def index(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_read(project))
    validate_cache(last_modified=project.updated_at)
    query = Schema.all()
    query = query.filter_by(project=project)
    pager = Pager(query, slug=slug)
    return jsonify(pager, index=not arg_bool('full'))


@blueprint.route('/api/1/projects/<slug>/schemata', methods=['POST', 'PUT'])
def create(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    data = request_data({'project': project})
    schema = schemata.save(data)
    db.session.commit()
    return jsonify(schema, status=201)


@blueprint.route('/api/1/projects/<slug>/schemata/<name>', methods=['GET'])
def view(slug, name):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_read(project))
    if not project.private:
        validate_cache(last_modified=project.updated_at)
    schema = object_or_404(Schema.by_name(project, name))
    return jsonify(schema)


@blueprint.route('/api/1/projects/<slug>/schemata/<name>',
                 methods=['POST', 'PUT'])
def update(slug, name):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    schema = object_or_404(Schema.by_name(project, name))
    data = request_data({'project': project})
    schema = schemata.save(data, schema=schema)
    db.session.commit()
    return jsonify(schema)


@blueprint.route('/api/1/projects/<slug>/schemata/<name>', methods=['DELETE'])
def delete(slug, name):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    schema = object_or_404(Schema.by_name(project, name))
    deleted = schemata.delete(schema)
    db.session.commit()
    if deleted:
        raise Gone()
    else:
        return jsonify(schema)
