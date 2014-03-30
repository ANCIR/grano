from grano.core import db
from grano.model.common import IntBase
from grano.model.util import slugify_column
from grano.model.attribute import Attribute
from grano.model.property import Property


class Schema(db.Model, IntBase):
    __tablename__ = 'grano_schema'

    name = db.Column(db.Unicode())
    label = db.Column(db.Unicode())
    label_in = db.Column(db.Unicode())
    label_out = db.Column(db.Unicode())
    hidden = db.Column(db.Boolean())
    obj = db.Column(db.Unicode())

    attributes = db.relationship(Attribute, backref='schema', lazy='joined',
        cascade='all, delete, delete-orphan')
    properties = db.relationship(Property, backref='schema', lazy='dynamic',
        cascade='all, delete, delete-orphan')
    relations = db.relationship('Relation', backref='schema', lazy='dynamic',
        cascade='all, delete, delete-orphan')
    project_id = db.Column(db.Integer, db.ForeignKey('grano_project.id'))

    def get_attribute(self, name):
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute

    @classmethod
    def by_name(cls, project, name):
        q = db.session.query(cls).filter_by(name=name)
        q = q.filter_by(project=project)
        return q.first()


    @classmethod
    def by_obj_name(cls, project, obj, name):
        q = db.session.query(cls)
        q = q.filter_by(project=project)
        q = q.filter_by(name=name)
        q = q.filter_by(obj=obj)
        return q.first()
