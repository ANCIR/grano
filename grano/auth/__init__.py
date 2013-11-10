import inspect
from flask import request

from grano.exc import Forbidden
import project


def logged_in():
    return request.user is not None


def user_id(id):
    return logged_in() and request.user.id == id


class Requirement(object):
    """ Checks a function call and raises an exception if the
    function returns a non-True value. """

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, attr):
        real = getattr(self.wrapped, attr)
        return Requirement(real)

    def __call__(self, *args, **kwargs):
        fc = self.wrapped(*args, **kwargs)
        if fc is not True:
            raise Forbidden('Sorry, you\'re not permitted to do this.')
        return fc

    @classmethod
    def here(cls):
        module = inspect.getmodule(cls)
        return cls(module)

require = Requirement.here()
