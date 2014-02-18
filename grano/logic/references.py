import colander

from grano.lib.exc import BadRequest
from grano.model import Project, Entity, Account
from grano.model import Schema


class Ref(object):
    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        return None

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null
        return self.decode(node, cstruct)

    def cstruct_children(self, node, cstruct):
        return []

    def get(self, cstruct):
        if cstruct is None:
            raise BadRequest()
        project = self.decode(None, cstruct)
        if project is None:
            raise BadRequest()
        return project


class ProjectRef(Ref):

    def decode(self, node, cstruct):
        if isinstance(cstruct, Project):
            return cstruct
        if isinstance(cstruct, basestring):
            return Project.by_slug(cstruct)
        if isinstance(cstruct, dict):
            if cstruct.get('slug'):
                return Project.by_slug(cstruct.get('slug'))
        return None


class EntityRef(Ref):

    def __init__(self, project):
        self.project = project

    def decode(self, node, cstruct):
        if isinstance(cstruct, Entity):
            return cstruct
        if isinstance(cstruct, basestring):
            return Entity.by_id(self.project, cstruct)
        if isinstance(cstruct, dict):
            if cstruct.get('id'):
                return Entity.by_id(self.project, cstruct.get('id'))
        return None


class AccountRef(Ref):
    
    def decode(self, node, cstruct):
        if isinstance(cstruct, Account):
            return cstruct
        if isinstance(cstruct, basestring):
            return Account.by_login(cstruct)
        if isinstance(cstruct, dict):
            if cstruct.get('login'):
                return Account.by_login(cstruct.get('login'))
        return None


class SchemaRef(Ref):

    def __init__(self, project):
        self.project = project

    def decode(self, node, cstruct):
        if isinstance(cstruct, Schema):
            return cstruct
        if isinstance(cstruct, basestring):
            return Schema.by_name(self.project, cstruct)
        if isinstance(cstruct, dict):
            if cstruct.get('name'):
                return Schema.by_name(self.project,
                    cstruct.get('name'))
        return None
