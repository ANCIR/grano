from grano.core import db
from grano.model.common import IntBase


class Property(db.Model, IntBase):
    __tablename__ = 'property'

    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'))
    name = db.Column(db.Unicode(), index=True)
    value = db.Column(db.Unicode())
    source_url = db.Column(db.Unicode())
    active = db.Column(db.Boolean())

    obj = db.Column(db.String(20))
    __mapper_args__ = {'polymorphic_on': obj}

    def _apply_properties(self, name, prop):
        self.name = name
        self.schema = prop.get('schema')
        self.value = prop.get('value')
        self.source_url = prop.get('source_url')
        self.active = prop.get('active')
        db.session.add(self)


class EntityProperty(Property):
    __mapper_args__ = {'polymorphic_identity': 'entity'}

    entity_id = db.Column(db.Unicode(), db.ForeignKey('entity.id'), index=True)

    @classmethod
    def save(cls, entity, name, prop):
        obj = cls()
        obj.entity = entity
        obj._apply_properties(name, prop)


class RelationProperty(Property):
    __mapper_args__ = {'polymorphic_identity': 'relation'}

    relation_id = db.Column(db.Unicode(), db.ForeignKey('relation.id'),
                            index=True)

    @classmethod
    def save(cls, relation, name, prop):
        obj = cls()
        obj.relation = relation
        obj._apply_properties(name, prop)
