from grano.core import db
from grano.model.common import UUIDBase


class Relation(db.Model, UUIDBase):
    OBJ = __tablename__ = 'relation'

    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'), index=True)
    source_id = db.Column(db.Unicode, db.ForeignKey('entity.id'), index=True)
    target_id = db.Column(db.Unicode, db.ForeignKey('entity.id'), index=True)

    properties = db.relationship('EntityProperty', backref='entity', lazy='dynamic')


