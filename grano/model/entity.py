from grano.core import db, url_for
from grano.model.common import UUIDBase
from grano.model.property import Property, PropertyBase


class Entity(db.Model, UUIDBase, PropertyBase):
    __tablename__ = 'grano_entity'

    same_as = db.Column(db.Unicode, db.ForeignKey('grano_entity.id'),
                        nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('grano_project.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))
    schema_id = db.Column(db.Integer, db.ForeignKey('grano_schema.id'),
                          index=True)

    degree_in = db.Column(db.Integer)
    degree_out = db.Column(db.Integer)
    degree = db.Column(db.Integer)

    inbound = db.relationship('Relation', lazy='dynamic', backref='target',
                              primaryjoin='Entity.id==Relation.target_id',
                              cascade='all, delete, delete-orphan')
    outbound = db.relationship('Relation', lazy='dynamic', backref='source',
                               primaryjoin='Entity.id==Relation.source_id',
                               cascade='all, delete, delete-orphan')

    properties = db.relationship(Property, backref='entity',
                                 order_by=Property.created_at.desc(),
                                 cascade='all, delete, delete-orphan',
                                 lazy='joined')

    @property
    def names(self):
        return [p for p in self.properties if p.name == 'name']

    @classmethod
    def by_name(cls, project, name, only_active=False):
        q = cls.by_name_many(project, name, only_active=only_active)
        return q.first()

    @classmethod
    def by_name_many(cls, project, name, only_active=False):
        q = db.session.query(cls)
        q = q.filter(cls.project == project)
        q = cls._filter_property(q, 'name', name, only_active=only_active)
        return q

    # @classmethod
    # def by_id_many(cls, ids, account=None):
    #     from grano.model import Project, Permission
    #     q = db.session.query(cls)
    #     q = q.filter(cls.id.in_(ids))
    #     if account is not None:
    #         q = q.join(Project)
    #         q = q.outerjoin(Permission)
    #         q = q.filter(or_(Project.private == False, # noqa
    #             and_(Permission.reader == True, Permission.account == account)))
    #     id_map = {}
    #     for e in q.all():
    #         id_map[e.id] = e
    #     return id_map

    def to_dict_index(self):
        """ Convert an entity to the REST API form. """
        data = {
            'id': self.id,
            'degree': self.degree,
            'degree_in': self.degree_in,
            'degree_out': self.degree_out,
            'project': self.project.to_dict_index(),
            'schema': self.schema.to_dict_index(),
            'api_url': url_for('entities_api.view', id=self.id),
            'properties': {}
        }

        for prop in self.active_properties:
            name, prop = prop.to_dict_kv()
            data['properties'][name] = prop

        if self.same_as:
            data['same_as'] = self.same_as
            data['same_as_url'] = url_for('entities_api.view', id=self.same_as)
        return data

    def to_dict(self):
        """ Full serialization of the entity. """
        data = self.to_dict_index()
        data['created_at'] = self.created_at
        data['updated_at'] = self.updated_at

        if data['degree_in'] > 0:
            data['inbound_url'] = url_for('relations_api.index', target=self.id)

        if data['degree_out'] > 0:
            data['outbound_url'] = url_for('relations_api.index', source=self.id)
        return data

    def to_index(self):
        """ Convert an entity to a form appropriate for search indexing. """
        data = self.to_dict()

        data['names'] = []
        for prop in self.properties:
            if prop.name == 'name':
                data['names'].append(prop.value)

        return data
