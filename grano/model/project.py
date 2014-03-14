from grano.core import db
from grano.model.util import make_token, MutableDict, JSONEncodedDict
from grano.model.common import IntBase


class Project(db.Model, IntBase):
    __tablename__ = 'project'

    slug = db.Column(db.Unicode)
    label = db.Column(db.Unicode)
    private = db.Column(db.Boolean)
    settings = db.Column(MutableDict.as_mutable(JSONEncodedDict))

    author_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    relations = db.relationship('Relation', backref='project', lazy='dynamic')
    entities = db.relationship('Entity', backref='project', lazy='dynamic')
    schemata = db.relationship('Schema', backref='project', lazy='dynamic')
    permissions = db.relationship('Permission', backref='project', lazy='dynamic')
    

    @classmethod
    def by_slug(cls, slug):
        q = db.session.query(cls).filter_by(slug=slug)
        return q.first()
