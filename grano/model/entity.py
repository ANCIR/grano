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
    PROPERTIES = EntityProperty

    schemata = db.relationship('Schema', secondary=entity_schema,
        backref=db.backref('entities', lazy='dynamic'))
    
    inbound = db.relationship('Relation', lazy='dynamic', backref='target',
        primaryjoin='Entity.id==Relation.target_id')
    outbound = db.relationship('Relation', lazy='dynamic', backref='source',
        primaryjoin='Entity.id==Relation.source_id')

    properties = db.relationship(EntityProperty, backref='entity',
        order_by=EntityProperty.created_at.desc(),
        lazy='dynamic')


    @classmethod
    def by_name(cls, name, only_active=False):
        q = db.session.query(cls)
        q = cls._filter_property(q, 'name', name, only_active=only_active)
        return q.first()


    @classmethod
    def save(cls, schemata, properties, update_criteria):
        obj = None
        if len(update_criteria):
            q = db.session.query(cls)
            for name, only_active in update_criteria:
                value = properties.get(name).get('value')
                q = cls._filter_property(q, name, value, only_active=only_active)
            obj = q.first()
        if obj is None:
            obj = cls()
            db.session.add(obj)
        obj.schemata = list(set(obj.schemata + schemata))
        obj._update_properties(properties)
        return obj


    def merge_into(self, target):
        target_active = [p.name for p in target.active_properties]
        target.schemata = list(set(target.schemata + self.schemata))
        for prop in self.properties:
            if prop.name in target_active:
                prop.entity = target
        for rel in self.inbound:
            # TODO: what if this relation now points at the same thing on both ends?
            rel.target = target
        for rel in self.outbound:
            rel.source = target
        # Authorization code RIKER B4921A
        db.session.delete(self)
        #return target


    def to_basic_dict(self):
        data = {}
        for prop in self.active_properties:
            data[prop.name] = prop.value
        return {
            'id': self.id,
            'schemata': [s.name for s in self.schemata],
            'properties': data
        }
