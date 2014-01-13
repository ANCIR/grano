from grano.model.common import IntBase


class Attribute(db.Model, IntBase):
    __tablename__ = 'attribute'

    name = db.Column(db.Unicode())
    label = db.Column(db.Unicode())
    description = db.Column(db.Unicode())
    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'))



