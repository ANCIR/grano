from grano.core import db
from grano.model.common import IntBase
from grano.model.util import slugify_column


class Attribute(db.Model, IntBase):
    __tablename__ = 'attribute'

    name = db.Column(db.Unicode())
    label = db.Column(db.Unicode())
    description = db.Column(db.Unicode())
    hidden = db.Column(db.Boolean())
    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'))


    def to_dict(self):
        return {
            'name': self.name,
            'label': self.label,
            'hidden': self.hidden,
            'description': self.description
        }


    @classmethod
    def by_name(cls, schema, name):
        q = db.session.query(cls)
        q = q.filter_by(schema=schema)
        q = q.filter_by(name=name)
        return q.first()


    @classmethod
    def from_dict(cls, data):
        schema = data.get('schema')
        name = slugify_column(data.get('name', data.get('label')))
        obj = cls.by_name(schema, name)
        if obj is None:
            obj = cls()
        obj.name = name
        obj.label = data.get('label')
        obj.hidden = data.get('hidden')
        obj.description = data.get('description')
        obj.schema = schema
        db.session.add(obj)
        return obj
