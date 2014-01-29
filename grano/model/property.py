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

    def to_dict(self):
        return {
            'name': self.name,
            'schema': self.schema.name,
            'value': self.value,
            'source_url': self.source_url,
            'active': self.active
        }


class EntityProperty(Property):
    __mapper_args__ = {'polymorphic_identity': 'entity'}

    entity_id = db.Column(db.Unicode(), db.ForeignKey('entity.id'), index=True)

    def _set_obj(self, obj):
        self.entity = obj


class RelationProperty(Property):
    __mapper_args__ = {'polymorphic_identity': 'relation'}

    relation_id = db.Column(db.Unicode(), db.ForeignKey('relation.id'),
                            index=True)

    def _set_obj(self, obj):
        self.relation = obj
