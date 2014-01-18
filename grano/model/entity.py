from grano.core import db
from grano.model.common import UUIDBase

entity_schema = db.Table('entity_schema',
    db.Column('entity_id', db.Unicode, db.ForeignKey('entity.id')),
    db.Column('schema_id', db.Integer, db.ForeignKey('schema.id'))
)

class Entity(db.Model, UUIDBase):
    OBJ = __tablename__ = 'entity'

    schemata = db.relationship('Schema', secondary=entity_schema,
        backref=db.backref('entities', lazy='dynamic'))
    
    inbound = db.relationship('Entity', backref='target', lazy='dynamic')
    outbound = db.relationship('Entity', backref='source', lazy='dynamic')

    properties = db.relationship('EntityProperty', backref='entity', lazy='dynamic')

