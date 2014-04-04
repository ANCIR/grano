from StringIO import StringIO

from flask import Blueprint, render_template, request, Response
from flask import redirect, make_response, send_file
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased

from grano.lib.serialisation import jsonify
from grano.lib.exc import BadRequest
from grano.lib.args import object_or_404, request_data, get_limit
from grano.model import Project, File, Permission
from grano.logic import files
from grano.logic.references import ProjectRef
from grano.lib.pager import Pager
from grano.lib.exc import Gone, BadRequest
from grano.core import app, db, url_for
from grano.views.cache import validate_cache
from grano import authz


blueprint = Blueprint('files_api', __name__)


@blueprint.route('/api/1/files', methods=['GET'])
def index():
    query = File.all()
    query = query.join(Project)
    query = query.outerjoin(Permission)
    query = query.filter(or_(Project.private==False,
        and_(Permission.reader==True, Permission.account==request.account)))

    if request.args.get('project'):
        alias = aliased(Project)
        query = query.join(project, File.project)
        query = query.filter(Project.slug==request.args.get('project'))
    
    pager = Pager(query)
    validate_cache(keys=pager.cache_keys())
    conv = lambda es: [files.to_rest_index(e) for e in es]
    return jsonify(pager, index=True)


@blueprint.route('/api/1/files', methods=['POST', 'PUT'])
def create():
    data = request_data({'author': request.account})
    project = ProjectRef().get(data.get('project'))
    data['project'] = project
    authz.require(authz.project_edit(project))
    file_ = files.save(data, request.files.get('file'))
    db.session.commit()
    return jsonify(file_)


@blueprint.route('/api/1/files/<id>', methods=['GET'])
def view(id):
    file = object_or_404(File.by_id(id))
    authz.require(authz.project_read(file.project))
    return jsonify(file)


@blueprint.route('/api/1/files/<id>/_serve', methods=['GET'])
def serve(id):
    file = object_or_404(File.by_id(id))
    authz.require(authz.project_read(file.project))
    sio = StringIO()
    sio.write(file.data)
    sio.seek(0)
    return send_file(sio,
        attachment_filename=file.file_name,
        as_attachment=False)


@blueprint.route('/api/1/files/<id>/_table', methods=['GET'])
def table(id):
    file = object_or_404(File.by_id(id))
    authz.require(authz.project_read(file.project))
    limit = get_limit(10)
    validate_cache(keys={'id': file.id, 'limit': limit})
    return jsonify(files.as_table(file, limit))


@blueprint.route('/api/1/files/<id>', methods=['DELETE'])
def delete(id):
    file_ = object_or_404(File.by_id(id))
    authz.require(authz.project_edit(file_.project))
    entities.delete(file_)
    db.session.commit()
    raise Gone()
