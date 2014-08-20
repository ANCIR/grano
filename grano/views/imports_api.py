from flask import Blueprint, request

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Project
from grano.logic import imports
from grano import authz


blueprint = Blueprint('imports_api', __name__)


@blueprint.route('/api/1/projects/<slug>/_import', methods=['POST'])
def perform_import(slug):
    project = object_or_404(Project.by_slug(slug))
    authz.require(authz.project_edit(project))
    data = request_data({'project': project})
    pipeline = imports.make_importer(project, request.account, data)
    return jsonify(pipeline)
