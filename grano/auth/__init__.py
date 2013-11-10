import inspect
from flask import request
from flask.ext.utils.authz import Requirement

from grano.exc import Forbidden
import project


def logged_in():
    return request.user is not None


def user_id(id):
    return logged_in() and request.user.id == id

require = Requirement.here()
