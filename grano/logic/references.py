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

    def __init__(self, project=None):
        self.project = project

    def decode(self, node, cstruct):
        if isinstance(cstruct, Entity):
            if cstruct.project == self.project:
                return cstruct
        if isinstance(cstruct, basestring):
            entity = Entity.by_id(cstruct)
            if entity.project == self.project:
                return entity
        if isinstance(cstruct, dict):
            if cstruct.get('id'):
                entity = Entity.by_id(cstruct.get('id'))
                if self.project is None:
                    return entity
                if entity is not None and entity.project == self.project:
                    return entity
        return None


class AccountRef(Ref):
    
    def decode(self, node, cstruct):
        if isinstance(cstruct, Account):
            return cstruct
        if isinstance(cstruct, int):
            return Account.by_id(cstruct)
        if isinstance(cstruct, dict):
            if cstruct.get('id'):
                return Account.by_id(cstruct.get('id'))
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
