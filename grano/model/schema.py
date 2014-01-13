from grano.model.common import IntBase


class Schema(db.Model, IntBase):
    __tablename__ = 'schema'

    slug = db.Column(db.Unicode())
    label = db.Column(db.Unicode())
    obj = db.Column(db.Unicode())

    attributes = db.relationship('Attribute', backref='schema', lazy='dynamic')

