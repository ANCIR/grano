from flask import Blueprint, render_template
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Schema, Project
from grano.logic import schemata
from grano.lib.pager import Pager
from grano.lib.exc import Gone
from grano.core import app, db
from grano import authz


blueprint = Blueprint('schemata_api', __name__)


@blueprint.route('/api/1/projects/<slug>/schemata', methods=['GET'])
def index(slug):
    project = object_or_404(Project.by_slug(slug))
    query = Schema.all()
    query = query.filter_by(project=project)
    pager = Pager(query)
    conv = lambda es: [schemata.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))


@blueprint.route('/api/1/projects/<slug>/schemata', methods=['POST', 'PUT'])
def create(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    schema = schemata.save(request_data())
    db.session.commit()
    return jsonify(schemata.to_rest(schema), status=201)


@blueprint.route('/api/1/projects/<slug>/schemata/<name>', methods=['GET'])
def view(slug, name):
    project = object_or_404(Project.by_slug(slug))
    schema = object_or_404(Schema.by_name(project, name))
    return jsonify(schemata.to_rest(schema))


@blueprint.route('/api/1/projects/<slug>/schemata/<name>', methods=['POST', 'PUT'])
def update(slug, name):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    schema = object_or_404(Schema.by_name(project, name))
    project = schemata.save(request_data(), schema=schema)
    db.session.commit()
    return jsonify(schemata.to_rest(schema))


@blueprint.route('/api/1/projects/<slug>/schemata/<name>', methods=['DELETE'])
def delete(slug, name):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_manage(project))
    schema = object_or_404(Schema.by_name(project, name))
    schemata.delete(schema)
    db.session.commit()
    raise Gone()
