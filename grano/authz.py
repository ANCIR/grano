from flask import request

from grano.core import db
from grano.model import Permission, Project
from grano.lib.exc import Forbidden


def permissions():
    """ Cache the full matrix of which projects this user has access to. """
    if not hasattr(request, 'permissions'):
        matrix = {
            'reader': set(),
            'editor': set(),
            'admin': set()
        }
        q = db.session.query(Project.id)
        q = q.filter(Project.private == False)
        matrix['reader'].update([id for id, in q.all()])

        if logged_in():
            q = Permission.all()
            q = q.filter_by(account=request.account)
            for perm in q.all():
                if perm.reader:
                    matrix['reader'].add(perm.project_id)
                if perm.editor:
                    matrix['editor'].add(perm.project_id)
                if perm.admin:
                    matrix['admin'].add(perm.project_id)
        request.permissions = matrix
    return request.permissions


def _find_permission(project):
    q = Permission.all()
    q = q.filter_by(project=project)
    q = q.filter_by(account=request.account)
    return q


def logged_in():
    return request.account is not None


def project_create():
    return logged_in()


def project_read(project):
    return project.id in permissions().get('reader')


def project_edit(project):
    return project.id in permissions().get('editor')


def project_manage(project):
    return project.id in permissions().get('admin')


def project_delete(project):
    return project_manage(project)

# Entity


def entity_create():
    return logged_in()


def entity_read(entity):
    return entity.project_id in permissions().get('reader')


def entity_edit(entity):
    return entity.project_id in permissions().get('editor')


def entity_manage(entity):
    return entity.project_id in permissions().get('admin')


def entity_delete(entity):
    return entity_manage(entity)


def relation_read(relation):
    return relation.project_id in permissions().get('reader')


def relation_edit(relation):
    return relation.project_id in permissions().get('editor')


def relation_manage(relation):
    return relation.project_id in permissions().get('admin')


def require(pred):
    if not pred:
        raise Forbidden("Sorry, you're not permitted to do this!")
