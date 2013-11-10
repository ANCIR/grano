from flask import Blueprint, request, session, redirect
from flask import url_for

from flask.ext.login import current_user

from grano.model import Project
from grano.auth import require
from grano.views.pager import query_pager
from grano.views.util import jsonify, obj_or_404


blueprint = Blueprint('projects', __name__)


@blueprint.route('/projects')
def index():
    """ List projects. """
    return query_pager(Project.objects, 'projects.index')


@blueprint.route('/projects', methods=['POST'])
def create():
    """ Create a new project. """
    data = request_content(request)
    dataset = logic.dataset.create(owner, data)
    return redirect(url_for('.get', owner=owner, 
                            dataset=dataset.name))


@blueprint.route('/projects/<slug>')
def get(slug):
    project = obj_or_404(Project.by_slug(slug))
    require.project.view(project)
    return jsonify(project)

