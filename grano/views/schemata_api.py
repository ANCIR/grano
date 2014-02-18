from flask import Blueprint, render_template
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404
from grano.model import Schema, Project
from grano.logic import schemata
from grano.lib.pager import Pager
from grano.core import app


blueprint = Blueprint('schemata_api', __name__)


@blueprint.route('/api/1/projects/<slug>/schemata', methods=['GET'])
def index(slug):
    project = object_or_404(Project.by_slug(slug))
    query = Schema.all()
    query = query.filter_by(project=project)
    pager = Pager(query)
    conv = lambda es: [schemata.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))


@blueprint.route('/api/1/projects/<slug>/schemata/<name>', methods=['GET'])
def view(slug, name):
    project = object_or_404(Project.by_slug(slug))
    schema = object_or_404(Schema.by_name(project, name))
    return jsonify(schemata.to_rest(schema))
