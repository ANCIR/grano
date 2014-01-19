
from grano.core import db
from grano.model import Schema, Entity, Relation


class SchemaCache(object):
    # TODO: move to model?
    SCHEMATA = {}

    @classmethod
    def get(cls, type, name):
        obj = type.OBJ
        if not (obj, name) in cls.SCHEMATA:
            schema = Schema.by_obj_name(obj, name)
            if schema is None:
                raise ValueError("Unknown schema: %s" % name)
            cls.SCHEMATA[(obj, name)] = schema
        return cls.SCHEMATA[(obj, name)]


class ObjectLoader(object):

    def _setup(self, type, schemata):
        self.schemata = [SchemaCache.get(type, s) for s in schemata]
        self.properties = {}

    def get_schema(self, name):
        for schema in self.schemata:
            for attribute in schema.attributes:
                if attribute.name == name:
                    yield schema

    @property
    def attributes(self):
        for schema in self.schemata:
            for attribute in schema.attributes:
                yield attribute

    @property
    def attribute_names(self):
        for attribute in self.attributes:
            yield attribute.name

    def set(self, name, value, source_url=None, active=True, key=False):
        schema = self.get_schema(name)
        if name is None:
            raise ValueError('Invalud attribute name: %s' % name)
        self.properties[name] = {
            'name': name,
            'value': value if value is None else unicode(value),
            'source_url': source_url or self.source_url,
            'active': active,
            'schema': schema,
            'key': key
            }


class EntityLoader(ObjectLoader):
    
    def __init__(self, schemata, source_url=None):
        self._setup(Entity, set(schemata + ['base']))
        self.source_url = source_url
        self._entity = None

    @property
    def entity(self):
        if self._entity is None:
            self.save()
        return self._entity

    def save(self):
        #print Entity.by_property('name', self.properties.get('name').get('value'))
        self._entity = Entity.save(self.schemata, self.properties)
        db.session.flush()


class RelationLoader(ObjectLoader):
    
    def __init__(self, schema, source, target, source_url=None):
        self._setup(Relation, [schema])
        self.source_url = source_url
        self.source = source 
        self.target = target

    def save(self):
        self.relation = Relation.save(self.schemata.pop(),
            self.properties, self.source.entity, self.target.entity)
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
