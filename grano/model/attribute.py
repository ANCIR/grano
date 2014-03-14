from grano.core import db
from grano.model.common import IntBase
from grano.model.util import slugify_column


class Attribute(db.Model, IntBase):
    __tablename__ = 'grano_attribute'

    DATATYPES = {
        'string': 'value_string', 
        'integer': 'value_integer',
        'float': 'value_float',
        'datetime': 'value_datetime',
        'boolean': 'value_boolean'
        }

    name = db.Column(db.Unicode())
    label = db.Column(db.Unicode())
    description = db.Column(db.Unicode())
    hidden = db.Column(db.Boolean())
    datatype = db.Column(db.Unicode())
    
    schema_id = db.Column(db.Integer, db.ForeignKey('grano_schema.id'))
    properties = db.relationship('Property', backref='attribute', lazy='dynamic')

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

