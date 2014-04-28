from sqlalchemy import or_, and_

from grano.core import db, url_for
from grano.model.common import UUIDBase, PropertyBase
from grano.model.schema import Schema
from grano.model.property import EntityProperty


entity_schema = db.Table('grano_entity_schema',
    db.Column('entity_id', db.Unicode, db.ForeignKey('grano_entity.id')),
    db.Column('schema_id', db.Integer, db.ForeignKey('grano_schema.id'))
)


class Entity(db.Model, UUIDBase, PropertyBase):
    __tablename__ = 'grano_entity'
    PropertyClass = EntityProperty

    same_as = db.Column(db.Unicode, db.ForeignKey('grano_entity.id'),
                        nullable=True)
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
        q = q.filter(cls.project == project)
        attr = project.get_attribute('entity', 'name')
        q = cls._filter_property(q, [attr], name, only_active=only_active)
        return q.first()

    @classmethod
    def by_id_many(cls, ids, account=None):
        from grano.model import Project, Permission
        q = db.session.query(cls)
        q = q.filter(cls.id.in_(ids))
        if account is not None:
            q = q.join(Project)
            q = q.outerjoin(Permission)
            q = q.filter(or_(Project.private == False, # noqa
                and_(Permission.reader == True, Permission.account == account)))
        id_map = {}
        for e in q.all():
            id_map[e.id] = e
        return id_map

    @property
    def inbound_schemata(self):
        q = db.session.query(Schema)
        q = q.join(Schema.relations)
        q = q.filter(Relation.target_id == self.id)
        return q.distinct()

    def inbound_by_schema(self, schema):
        q = self.inbound.filter_by(schema=schema)
        return q

    @property
    def outbound_schemata(self):
        from grano.model.relation import Relation
        q = db.session.query(Schema)
        q = q.join(Schema.relations)
        q = q.filter(Relation.source_id == self.id)
        return q.distinct()

    def outbound_by_schema(self, schema):
        q = self.outbound.filter_by(schema=schema)
        return q

    @property
    def degree(self):
        return self.inbound.count() + self.outbound.count()

    def to_dict_base(self):
        data = {
            'id': self.id,
            'project': self.project.to_dict_index(),
            'api_url': url_for('entities_api.view', id=self.id),
        }

        data['schemata'] = [s.to_dict_index() for s in self.schemata]

        if self.same_as:
            data['same_as'] = self.same_as
            data['same_as_url'] = url_for('entities_api.view', id=self.same_as)
        return data

    def to_dict_index(self):
        """ Convert an entity to the REST API form. """
        data = self.to_dict_base()
        data['properties'] = {}
        for prop in self.active_properties:
            name, prop = prop.to_dict_index()
            data['properties'][name] = prop
        return data

    def to_dict(self):
        """ Full serialization of the entity. """
        data = self.to_dict_base()
        data['created_at'] = self.created_at
        data['updated_at'] = self.updated_at

        data['properties'] = {}
        for prop in self.active_properties:
            name, prop = prop.to_dict()
            data['properties'][name] = prop

        data['inbound_relations'] = self.inbound.count()
        if data['inbound_relations'] > 0:
            data['inbound_url'] = url_for('relations_api.index', target=self.id)

        data['outbound_relations'] = self.outbound.count()
        if data['outbound_relations'] > 0:
            data['outbound_url'] = url_for('relations_api.index', source=self.id)
        return data

    def to_index(self):
        """ Convert an entity to a form appropriate for search indexing. """
        data = self.to_dict()
        data['degree'] = self.degree

        data['names'] = []
        for prop in self.properties:
            if prop.name == 'name':
                data['names'].append(prop.value)

        return data
