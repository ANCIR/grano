from flask import Blueprint, render_template, request, Response
from flask import redirect, make_response
from sqlalchemy import or_, and_

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404
from grano.model import Project, Permission, Pipeline
from grano.lib.pager import Pager
from grano.core import app, db, url_for
from grano.views.cache import validate_cache
from grano import authz


blueprint = Blueprint('pipelines_api', __name__)


@blueprint.route('/api/1/pipelines', methods=['GET'])
def index():
    query = Pipeline.all()
    query = query.join(Project)
    query = query.outerjoin(Permission)
    query = query.filter(or_(Project.private==False,
        and_(Permission.reader==True, Permission.account==request.account)))

    if request.args.get('project'):
        query = query.filter(Project.slug==request.args.get('project'))

    if request.args.get('operation'):
        query = query.filter(Pipeline.operation==request.args.get('operation'))
    
    query = query.order_by(Pipeline.updated_at.desc())
    query = query.distinct()
    
    pager = Pager(query)
    validate_cache(keys=pager.cache_keys())
    return jsonify(pager, index=True)


@blueprint.route('/api/1/pipelines/<id>', methods=['GET'])
def view(id):
    pipeline = object_or_404(Pipeline.by_id(id))
    authz.require(authz.project_read(pipeline.project))
    return jsonify(pipeline)
