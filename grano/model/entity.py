from sqlalchemy import or_, and_

from grano.core import db
from grano.model.common import UUIDBase, PropertyBase
from grano.model.schema import Schema
from grano.model.relation import Relation
from grano.model.property import EntityProperty


entity_schema = db.Table('grano_entity_schema',
    db.Column('entity_id', db.Unicode, db.ForeignKey('grano_entity.id')),
    db.Column('schema_id', db.Integer, db.ForeignKey('grano_schema.id'))
)


class Entity(db.Model, UUIDBase, PropertyBase):
    __tablename__ = 'grano_entity'
    PropertyClass = EntityProperty

    same_as = db.Column(db.Unicode, db.ForeignKey('grano_entity.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('grano_project.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))

    schemata = db.relationship('Schema', secondary=entity_schema,
        backref=db.backref('entities', lazy='dynamic'))
    
    inbound = db.relationship('Relation', lazy='dynamic', backref='target',
        primaryjoin='Entity.id==Relation.target_id',
        cascade='all, delete, delete-orphan')
    outbound = db.relationship('Relation', lazy='dynamic', backref='source',
        primaryjoin='Entity.id==Relation.source_id',
        cascade='all, delete, delete-orphan')

    properties = db.relationship(EntityProperty, backref='entity',
        order_by=EntityProperty.created_at.desc(),
        cascade='all, delete, delete-orphan',
        lazy='joined')

    @property
    def names(self):
        return [p for p in self.properties if p.name == 'name']

    @classmethod
    def by_name(cls, project, name, only_active=False):
        q = db.session.query(cls)
        a = q.filter(cls.project==project)
        attr = project.get_attribute('entity', 'name')
        q = cls._filter_property(q, [attr], name, only_active=only_active)
        return q.first()

    @classmethod
    def by_id_many(cls, ids, account):
        from grano.model import Project, Permission
        q = db.session.query(cls)
        q = q.join(Project)
        q = q.outerjoin(Permission)
        q = q.filter(cls.id.in_(ids))
        q = q.filter(or_(Project.private==False,
            and_(Permission.reader==True, Permission.account==account)))

        id_map = {}
        for e in q.all():
            id_map[e.id] = e
        return id_map

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



