from StringIO import StringIO

from flask import Blueprint, request
from flask import send_file
from restpager import Pager
from sqlalchemy import or_, and_

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data, get_limit
from grano.model import Project, File, Permission
from grano.logic import files, entities
from grano.logic.references import ProjectRef
from grano.lib.exc import Gone
from grano.core import db
from grano.views.cache import validate_cache
from grano import authz


blueprint = Blueprint('files_api', __name__)


@blueprint.route('/api/1/files', methods=['GET'])
def index():
    query = File.all()
    query = query.join(Project)
    query = query.outerjoin(Permission)
    query = query.filter(or_(Project.private == False, # noqa
        and_(Permission.reader == True, # noqa
             Permission.account == request.account)))

    if request.args.get('project'):
        query = query.filter(Project.slug == request.args.get('project'))

    query = query.distinct()
    pager = Pager(query)
    validate_cache(keys=pager.cache_keys())
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
    res = send_file(sio, mimetype=file.mime_type)
    res.headers['Content-Disposition'] = 'filename=%s' % file.file_name
    return res


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
