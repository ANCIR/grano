from grano.core import db
from grano.model.common import IntBase


class Property(db.Model, IntBase):
    __tablename__ = 'property'

    name = db.Column(db.Unicode(), index=True)
    value = db.Column(db.Unicode())
    obj_id = db.Column(db.Unicode(), index=True)

    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'))
    source_url = db.Column(db.Unicode())

    active = db.Column(db.Boolean())
