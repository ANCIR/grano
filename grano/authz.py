from flask import request

from grano.lib.exc import Forbidden

def logged_in():
    return request.account is not None


def project_create():
    return logged_in()


def project_edit(project):
    if not logged_in():
        return False
    if project.public_edit:
        return True
    if project.owner_id == request.account.id:
        return True
    return False


def project_manage(project):
    if not logged_in():
        return False
    if project.owner_id == request.account.id:
        return True
    return False


def require(pred):
    if not pred:
        raise Forbidden("Sorry, you're not permitted to do this!")

