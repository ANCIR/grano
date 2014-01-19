from grano.core import db
from grano.model.common import UUIDBase, PropertyBase
from grano.model.property import RelationProperty


class Relation(db.Model, UUIDBase, PropertyBase):
    OBJ = __tablename__ = 'relation'

    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'), index=True)
    source_id = db.Column(db.Unicode, db.ForeignKey('entity.id'), index=True)
    target_id = db.Column(db.Unicode, db.ForeignKey('entity.id'), index=True)

    properties = db.relationship('EntityProperty', backref='relation', lazy='dynamic')


    @classmethod
    def save(cls, schema, properties, source, target):
        obj = cls()
        obj.source = source
        obj.target = target
        obj.schema = schema
        for name, prop in properties.items():
            RelationProperty.save(obj, name, prop)
        db.session.add(obj)
        return obj
