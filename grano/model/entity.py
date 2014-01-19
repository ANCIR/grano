from grano.core import db
from grano.model.common import UUIDBase, PropertyBase

from grano.model.relation import Relation
from grano.model.property import EntityProperty


entity_schema = db.Table('entity_schema',
    db.Column('entity_id', db.Unicode, db.ForeignKey('entity.id')),
    db.Column('schema_id', db.Integer, db.ForeignKey('schema.id'))
)


class Entity(db.Model, UUIDBase, PropertyBase):
    OBJ = __tablename__ = 'entity'

    schemata = db.relationship('Schema', secondary=entity_schema,
        backref=db.backref('entities', lazy='dynamic'))
    
    inbound = db.relationship('Relation', lazy='dynamic', backref='target',
        primaryjoin='Entity.id==Relation.target_id')
    outbound = db.relationship('Relation', lazy='dynamic', backref='source',
        primaryjoin='Entity.id==Relation.source_id')

    properties = db.relationship('EntityProperty', backref='entity',
        lazy='dynamic')


    @classmethod
    def save(cls, schemata, properties):
        obj = cls()
        obj.schemata = list(set(obj.schemata + schemata))
        for name, prop in properties.items():
            EntityProperty.save(obj, name, prop)
        db.session.add(obj)
        return obj
