from grano.core import db
from grano.model.common import UUIDBase, PropertyBase

from grano.model.schema import Schema
from grano.model.relation import Relation
from grano.model.property import EntityProperty


entity_schema = db.Table('entity_schema',
    db.Column('entity_id', db.Unicode, db.ForeignKey('entity.id')),
    db.Column('schema_id', db.Integer, db.ForeignKey('schema.id'))
)


class Entity(db.Model, UUIDBase, PropertyBase):
    __tablename__ = 'entity'
    PropertyClass = EntityProperty

    same_as = db.Column(db.Unicode, db.ForeignKey('entity.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    schemata = db.relationship('Schema', secondary=entity_schema,
        backref=db.backref('entities', lazy='dynamic'))
    
    inbound = db.relationship('Relation', lazy='dynamic', backref='target',
        primaryjoin='Entity.id==Relation.target_id')
    outbound = db.relationship('Relation', lazy='dynamic', backref='source',
        primaryjoin='Entity.id==Relation.source_id')

    properties = db.relationship(EntityProperty, backref='entity',
        order_by=EntityProperty.created_at.desc(),
        lazy='joined')

    @property
    def names(self):
        return [p for p in self.properties if p.name == 'name']

    @classmethod
    def by_name(cls, name, only_active=False):
        q = db.session.query(cls)
        q = cls._filter_property(q, 'name', name, only_active=only_active)
        return q.first()

    @property
    def inbound_schemata(self):
        from grano.model.relation import Relation
        q = db.session.query(Schema)
        q = q.join(Schema.relations)
        q = q.filter(Relation.target_id==self.id)
        return q.distinct()

    def inbound_by_schema(self, schema):
        q = self.inbound.filter_by(schema=schema)
        return q

    @property
    def outbound_schemata(self):
        from grano.model.relation import Relation
        q = db.session.query(Schema)
        q = q.join(Schema.relations)
        q = q.filter(Relation.source_id==self.id)
        return q.distinct()

    def outbound_by_schema(self, schema):
        q = self.outbound.filter_by(schema=schema)
        return q

    @property
    def degree(self):
        return self.inbound.count() + self.outbound.count()



