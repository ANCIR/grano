from grano.core import db, url_for
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

    attributes = db.relationship(Attribute, backref='schema', lazy='dynamic',
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


    def to_dict_index(self):
        return {
            'name': self.name,
            'label': self.label,
            'hidden': self.hidden,
            'obj': self.obj,
            'api_url': url_for('schemata_api.view', slug=self.project.slug, name=self.name)
        }


    def to_dict(self):
        data = self.to_dict_index()
        data['id'] = self.id
        data['project'] = self.project.to_dict_index()
        if self.label_in:
            data['label_in'] = self.label_in
        if self.label_out:
            data['label_out'] = self.label_out
        data['attributes'] = [a.to_dict() for a in self.attributes]
        return data
