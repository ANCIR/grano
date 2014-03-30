from grano.core import db
from grano.model.util import make_token, MutableDict, JSONEncodedDict
from grano.model.common import IntBase


class Project(db.Model, IntBase):
    __tablename__ = 'grano_project'

    slug = db.Column(db.Unicode)
    label = db.Column(db.Unicode)
    private = db.Column(db.Boolean, default=False)
    settings = db.Column(MutableDict.as_mutable(JSONEncodedDict))

    author_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))

    relations = db.relationship('Relation', backref='project', lazy='dynamic',
        cascade='all, delete, delete-orphan')
    entities = db.relationship('Entity', backref='project', lazy='dynamic',
        cascade='all, delete, delete-orphan')
    schemata = db.relationship('Schema', backref='project', lazy='dynamic',
        cascade='all, delete, delete-orphan')
    permissions = db.relationship('Permission', backref='project', lazy='dynamic',
        cascade='all, delete, delete-orphan')
    

    def get_attribute(self, obj, name):
        for schema in self.schemata:
            if schema.obj == obj:
                for attr in schema.attributes:
                    if attr.name == name:
                        return attr


    @classmethod
    def by_slug(cls, slug):
        q = db.session.query(cls).filter_by(slug=slug)
        return q.first()
