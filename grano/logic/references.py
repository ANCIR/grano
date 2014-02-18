import colander

from grano.model import Project, Entity, Account


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


class ProjectRef(Ref):

    def decode(self, node, cstruct):
        if isinstance(cstruct, Project):
            return cstruct
        if isinstance(cstruct, basestring):
            return Project.by_slug(cstruct)
        #elif isinstance(cstruct, int):
        #    project = Project.by_id(cstruct.get('id'))
        if isinstance(cstruct, dict):
            if cstruct.get('slug'):
                return Project.by_slug(cstruct.get('slug'))
            #elif cstruct.get('id'):
            #    project = Project.by_id(cstruct.get('id'))
        return None


class EntityRef(Ref):
    pass


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
    pass

