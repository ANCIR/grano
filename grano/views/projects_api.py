from flask import Blueprint, render_template
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404
from grano.model import Project
from grano.logic import projects
from grano.lib.pager import Pager
from grano.core import app


blueprint = Blueprint('projects_api', __name__)


@blueprint.route('/api/1/projects')
def index():
    query = Project.all()
    pager = Pager(query)
    conv = lambda es: [projects.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))


@blueprint.route('/api/1/projects/<slug>')
def view(slug):
    project = object_or_404(Project.by_slug(slug))
    return jsonify(projects.to_rest(project))
