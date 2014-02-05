from grano.core import db
from grano.model.common import IntBase
from grano.model.util import slugify_column
from grano.model.attribute import Attribute
from grano.model.property import Property


class Schema(db.Model, IntBase):
    __tablename__ = 'schema'
    SCHEMATA = {}

    name = db.Column(db.Unicode())
    label = db.Column(db.Unicode())
    label_in = db.Column(db.Unicode())
    label_out = db.Column(db.Unicode())
    hidden = db.Column(db.Boolean())
    obj = db.Column(db.Unicode())

    attributes = db.relationship(Attribute, backref='schema', lazy='joined')
    properties = db.relationship(Property, backref='schema', lazy='dynamic')
    relations = db.relationship('Relation', backref='schema', lazy='dynamic')


    def get_attribute(self, name):
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute


    @classmethod
    def cached(cls, type, name):
        obj = type.__tablename__
        if not (obj, name) in cls.SCHEMATA:
            schema = Schema.by_obj_name(obj, name)
            if schema is None:
                raise ValueError("Unknown schema: %s" % name)
            cls.SCHEMATA[(obj, name)] = schema
        return cls.SCHEMATA[(obj, name)]


    @classmethod
    def by_name(cls, name):
        q = db.session.query(cls).filter_by(name=name)
        return q.first()


    @classmethod
    def by_obj_name(cls, obj, name):
        q = db.session.query(cls)
        q = q.filter_by(name=name)
        q = q.filter_by(obj=obj)
        return q.first()


    def to_dict(self, shallow=False):
        data = {
            'id': self.id,
            'name': self.name,
            'label': self.label,
            'label_in': self.label_in,
            'label_out': self.label_out,
            'hidden': self.hidden,
            'obj': self.obj
        }
        if not shallow:
            data['attributes'] = [a.to_dict() for a in self.attributes]
        return data
