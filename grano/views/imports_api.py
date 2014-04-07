import colander
from flask import Blueprint, render_template, request, Response
from flask import redirect, make_response

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Project, Permission, Pipeline
from grano.lib.pager import Pager
from grano.logic import imports
from grano.core import app, db, url_for
from grano.views.cache import validate_cache
from grano import authz


blueprint = Blueprint('imports_api', __name__)


@blueprint.route('/api/1/projects/<slug>/_import', methods=['POST'])
def perform_import(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_edit(project))
    data = request_data({'project': project})
    pipeline = imports.make_importer(project, request.account, data)
    return jsonify(pipeline)
