import logging

from grano.core import db
from grano.model import Schema, Entity, Relation, Project
from grano.logic import entities, relations, projects, accounts
from grano.logic.validation import Invalid


log = logging.getLogger(__name__)


class ObjectLoader(object):
    # Abstract parent

    def _setup(self, loader, type, schemata):
        self.loader = loader
        self.schemata = [Schema.cached(loader.project, type, s) for s in schemata]
        self.properties = {}
        self.update_criteria = set()


    def unique(self, name, only_active=True):
        self.update_criteria.add((name, only_active))


    def set(self, name, value, source_url=None):
        source_url = source_url or self.source_url
        if source_url is None:
            log.warning('No source for property %s.', name)
        self.properties[name] = {
            'name': name,
            'value': value if value is None else unicode(value),
            'source_url': source_url,
            'active': True
            }


class EntityLoader(ObjectLoader):
    
    def __init__(self, loader, schemata, source_url=None):
        self._setup(loader, Entity, set(schemata + ['base']))
        self.unique('name', only_active=False)
        self.source_url = source_url
        self._entity = None


    @property
    def entity(self):
        if self._entity is None:
            self.save()
        return self._entity


    def save(self):
        try:
            self._entity = entities.save(self.loader.project, self.loader.account, 
                self.schemata, self.properties, self.update_criteria)
            db.session.flush()
        except Invalid, inv:
            log.warning("Validation error: %r", inv)


class RelationLoader(ObjectLoader):
    
    def __init__(self, loader, schema, source, target, source_url=None):
        self._setup(loader, Relation, [schema])
        self.source_url = source_url
        self.source = source 
        self.target = target


    def save(self):
        try:
            self._relation = relations.save(self.loader.project, self.loader.account, 
                self.schemata.pop(), self.properties, self.source.entity,
                self.target.entity, self.update_criteria)
            db.session.flush()
        except Invalid, inv:
            log.warning("Validation error: %r", inv)
        

class Loader(object):
    """ A loader is a factory object that can be used to make entities and 
    relations in the database. It will perform some validation and handle 
    database transactions. """

    def __init__(self, project_slug, source_url=None, project_label=None,
            project_settings=None):
        self.source_url = source_url
        self.account = accounts.console_account()
        self.project = projects.save(project_slug, self.account, label=project_label,
            settings=project_settings)
        self.entities = []
        self.relations = []


    def make_entity(self, schemata, source_url=None):
        entity = EntityLoader(self, schemata,
            source_url=source_url or self.source_url)
        self.entities.append(entity)
        return entity


    def make_relation(self, schema, source, target, source_url=None):
        relation = RelationLoader(self, schema, source, target,
            source_url=source_url or self.source_url)
        self.relations.append(relation)
        return relation


    def persist(self):
        db.session.commit()
