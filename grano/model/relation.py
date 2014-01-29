from grano.core import db
from grano.model.common import UUIDBase, PropertyBase
from grano.model.property import RelationProperty


class Relation(db.Model, UUIDBase, PropertyBase):
    __tablename__ = 'relation'
    PropertyClass = RelationProperty

    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'), index=True)
    source_id = db.Column(db.Unicode, db.ForeignKey('entity.id'), index=True)
    target_id = db.Column(db.Unicode, db.ForeignKey('entity.id'), index=True)

    properties = db.relationship(RelationProperty,
    	order_by=RelationProperty.created_at.desc(),
    	backref='relation', lazy='dynamic')


    def get_attribute(self, prop_name):
        for attribute in self.schema.attributes:
            if attribute.name == prop_name:
                return attribute
