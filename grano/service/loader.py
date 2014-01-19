
from grano.core import db
from grano.model import Schema, Entity, Relation


class ObjectLoader(object):
    # Abstract parent

    def _setup(self, type, schemata):
        self.schemata = [Schema.cached(type, s) for s in schemata]
        self.properties = {}
        self.update_criteria = set()

    def get_schema(self, name):
        for schema in self.schemata:
            for attribute in schema.attributes:
                if attribute.name == name:
                    yield schema

    def unique(self, name, only_active=True):
        self.update_criteria.add((name, only_active))

    def set(self, name, value, source_url=None, key=False):
        schema = self.get_schema(name)
        if name is None:
            raise ValueError('Invalud attribute name: %s' % name)
        self.properties[name] = {
            'name': name,
            'value': value if value is None else unicode(value),
            'source_url': source_url or self.source_url,
            'active': True,
            'schema': schema,
            'key': key
            }


class EntityLoader(ObjectLoader):
    
    def __init__(self, schemata, source_url=None):
        self._setup(Entity, set(schemata + ['base']))
        self.unique('name', only_active=False)
        self.source_url = source_url
        self._entity = None

    @property
    def entity(self):
        if self._entity is None:
            self.save()
        return self._entity

    def save(self):
        self._entity = Entity.save(self.schemata, self.properties,
            self.update_criteria)
        db.session.flush()


class RelationLoader(ObjectLoader):
    
    def __init__(self, schema, source, target, source_url=None):
        self._setup(Relation, [schema])
        self.source_url = source_url
        self.source = source 
        self.target = target

    def save(self):
        self.relation = Relation.save(self.schemata.pop(),
            self.properties, self.source.entity, self.target.entity,
            self.update_criteria)
        db.session.flush()


class Loader(object):
    """ A loader is a factory object that can be used to make entities and 
    relations in the database. It will perform some validation and handle 
    database transactions. """

    def __init__(self, source_url=None):
        self.source_url = source_url
        self.entities = []
        self.relations = []

    def make_entity(self, schemata, source_url=None):
        entity = EntityLoader(schemata,
            source_url=source_url or self.source_url)
        self.entities.append(entity)
        return entity

    def make_relation(self, schema, source, target, source_url=None):
        relation = RelationLoader(schema, source, target,
            source_url=source_url or self.source_url)
        self.relations.append(relation)
        return relation

    def persist(self):
        db.session.commit()
