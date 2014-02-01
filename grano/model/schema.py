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


    @classmethod
    def from_dict(cls, data):
        name = slugify_column(data.get('name', data.get('label')))
        obj = cls.by_name(name)
        if obj is None:
            obj = cls()
        obj.name = name
        obj.label = data.get('label')
        obj.label_in = data.get('label_in', obj.label)
        obj.label_out = data.get('label_out', obj.label)

        # TODO validate:
        obj.obj = data.get('obj')
        obj.hidden = data.get('hidden')
        db.session.add(obj)
        
        # TODO check that the name is unique across 'obj'
        names = []
        for attribute in data.get('attributes', []):
            attribute['schema'] = obj
            attr = Attribute.from_dict(attribute)
            obj.attributes.append(attr)
            names.append(attr.name)
        for attr in obj.attributes:
            if attr.name not in names:
                db.session.delete(attr)
        return obj


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
