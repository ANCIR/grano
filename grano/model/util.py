from grano.core import mongo


class ModelException(Exception):
    pass

class ObjectExists(ModelException):
    pass