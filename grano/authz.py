from flask import request

from grano.model import Permission
from grano.lib.exc import Forbidden


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
    if not logged_in():
        return False
    q = _find_permission(project).filter_by(reader=True)
    return q.count() > 0


def project_edit(project):
    if not logged_in():
        return False
    q = _find_permission(project).filter_by(editor=True)
    return q.count() > 0


def project_manage(project):
    if not logged_in():
        return False
    q = _find_permission(project).filter_by(admin=True)
    return q.count() > 0


def project_delete(project):
    return project_manage(project)


def require(pred):
    if not pred:
        raise Forbidden("Sorry, you're not permitted to do this!")

