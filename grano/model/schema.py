from grano.core import db
from grano.model.common import IntBase, slugify_column
from grano.model.attribute import Attribute


class Schema(db.Model, IntBase):
    __tablename__ = 'schema'

    name = db.Column(db.Unicode())
    label = db.Column(db.Unicode())
    obj = db.Column(db.Unicode())

    attributes = db.relationship(Attribute, backref='schema', lazy='dynamic')


    @classmethod
    def by_name(cls, name):
        q = db.session.query(cls).filter_by(name=name)
        return q.first()


    @classmethod
    def from_dict(cls, data):
    	name = slugify_column(data.get('name', data.get('label')))
    	obj = cls.by_name(name)
    	if obj is None:
    		obj = cls()
    	obj.name = name
    	obj.label = data.get('label')
    	obj.obj = data.get('obj')
    	db.session.add(obj)
    	for attribute in data.get('attributes', []):
    		attribute['schema']
    		obj.attributes.append(Attribute.from_dict(attribute))
    	return obj


    def to_dict(self):
    	return {
    		'id': self.id,
    		'name': self.name,
    		'label': self.label,
    		'obj': self.obj
    		'attributes': [a.to_dict() for a in self.attributes]
    	}
