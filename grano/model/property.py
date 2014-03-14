from grano.core import db
from grano.model.common import IntBase
from grano.model.attribute import Attribute


class Property(db.Model, IntBase):
    __tablename__ = 'grano_property'

    schema_id = db.Column(db.Integer, db.ForeignKey('grano_schema.id'))
    attribute_id = db.Column(db.Integer, db.ForeignKey('grano_attribute.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))

    name = db.Column(db.Unicode(), index=True)
    
    value_string = db.Column(db.Unicode())
    value_integer = db.Column(db.Integer())
    value_float = db.Column(db.Float())
    value_datetime = db.Column(db.DateTime())
    value_boolean = db.Column(db.Boolean())

    source_url = db.Column(db.Unicode())
    active = db.Column(db.Boolean())

    @property
    def value(self):
        for column in Attribute.DATATYPES.values():
            value = getattr(self, column)
            if value is not None:
                return value


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

    entity_id = db.Column(db.Unicode(), db.ForeignKey('grano_entity.id'), index=True)

    def _set_obj(self, obj):
        self.entity = obj


class RelationProperty(Property):
    __mapper_args__ = {'polymorphic_identity': 'relation'}

    relation_id = db.Column(db.Unicode(), db.ForeignKey('grano_relation.id'),
                            index=True)

    def _set_obj(self, obj):
        self.relation = obj
