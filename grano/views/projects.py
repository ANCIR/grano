from flask import Blueprint, request, session, redirect
from flask import url_for

from flask.ext.login import current_user

from grano.model import Project
from grano.views.pager import query_pager
from grano.views.util import jsonify, obj_or_404


blueprint = Blueprint('projects', __name__)


@blueprint.route('/projects')
def index():
    return query_pager(Project.objects, 'projects.index')


@blueprint.route('/projects/<slug>')
def get(slug):
    project = obj_or_404(Project.by_id(id))
    #require.service.view(service)
    return jsonify(project)
