from flask import request

from grano.model import Permission
from grano.lib.exc import Forbidden

PUBLISHED_THRESHOLD = 5 # minimum status value for publication


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
    if not project.private:
        return True
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

# Entity

def entity_create():
    return logged_in()


def entity_read(entity):
    if not entity.project.private and entity.status >= PUBLISHED_THRESHOLD:
        return True
    q = _find_permission(entity.project).first()
    if q:
        if q.editor or q.admin:
            return True
        elif q.reader and entity.status >= PUBLISHED_THRESHOLD:
            return True
    return False


def entity_edit(entity):
    return project_edit(entity.project)


def entity_manage(entity):
    return project_manage(entity.project)


def entity_delete(entity):
    return entity_manage(entity)


def require(pred):
    if not pred:
        raise Forbidden("Sorry, you're not permitted to do this!")

