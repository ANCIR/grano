from grano.core import db
from grano.model.common import UUIDBase, PropertyBase
from grano.model.property import RelationProperty


class Relation(db.Model, UUIDBase, PropertyBase):
    __tablename__ = 'grano_relation'
    PropertyClass = RelationProperty

    schema_id = db.Column(db.Integer, db.ForeignKey('grano_schema.id'), index=True)
    source_id = db.Column(db.Unicode, db.ForeignKey('grano_entity.id'), index=True)
    target_id = db.Column(db.Unicode, db.ForeignKey('grano_entity.id'), index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('grano_project.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))

    properties = db.relationship(RelationProperty,
    	order_by=RelationProperty.created_at.desc(),
    	backref='relation', lazy='dynamic')

    @property
    def schemata(self):
        return [self.schema]

