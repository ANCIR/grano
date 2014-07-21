from grano.core import db
from grano.model.common import IntBase


class Attribute(db.Model, IntBase):
    __tablename__ = 'grano_attribute'

    DATATYPES = {
        'string': 'value_string',
        'integer': 'value_integer',
        'float': 'value_float',
        'datetime': 'value_datetime',
        'boolean': 'value_boolean',
        'file': 'value_file_id'
        }

    name = db.Column(db.Unicode())
    label = db.Column(db.Unicode())
    description = db.Column(db.Unicode())
    hidden = db.Column(db.Boolean())
    datatype = db.Column(db.Unicode())

    schema_id = db.Column(db.Integer, db.ForeignKey('grano_schema.id'))
    properties = db.relationship('Property', backref='attribute',
                                 cascade='all, delete, delete-orphan',
                                 lazy='dynamic')

    @property
    def value_column(self):
        return self.DATATYPES.get(self.datatype)

    @classmethod
    def all_named(cls, name):
        q = db.session.query(cls)
        q = q.filter_by(name=name)
        return q.all()

    @classmethod
    def by_schema_and_name(cls, schema, name):
        q = db.session.query(cls)
        q = q.filter_by(schema=schema)
        q = q.filter_by(name=name)
        return q.first()

    def to_index(self):
        return {
            'name': self.name,
            'label': self.label,
            'datatype': self.datatype
        }

    def to_dict(self):
        data = self.to_index()
        data['id'] = self.id
        data['hidden'] = self.hidden
        if self.description and len(self.description):
            data['description'] = self.description
        return data
