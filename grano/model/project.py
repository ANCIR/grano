from sqlalchemy import func

from grano.core import db, url_for
from grano.model.util import MutableDict, JSONEncodedDict
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
    pipelines = db.relationship('Pipeline', backref='project', lazy='dynamic',
                                cascade='all, delete, delete-orphan')
    schemata = db.relationship('Schema', backref='project', lazy='dynamic',
                               cascade='all, delete, delete-orphan')
    permissions = db.relationship('Permission', backref='project',
                                  lazy='dynamic',
                                  cascade='all, delete, delete-orphan')
    files = db.relationship('File', backref='project', lazy='dynamic',
                            cascade='all, delete, delete-orphan')

    @classmethod
    def by_slug(cls, slug):
        q = db.session.query(cls)
        q = q.filter(func.lower(cls.slug) == slug.lower())
        return q.first()

    def to_dict_index(self):
        return {
            'slug': self.slug,
            'label': self.label,
            'private': self.private,
            'api_url': url_for('projects_api.view', slug=self.slug),
            'entities_count': self.entities.count(),
            'relations_count': self.relations.count()
        }

    def to_dict(self):
        data = self.to_dict_index()
        data['settings'] = self.settings
        data['author'] = self.author.to_dict_index()
        data['schemata_index_url'] = url_for('schemata_api.index',
                                             slug=self.slug)
        data['entities_index_url'] = url_for('entities_api.index',
                                             project=self.slug)
        data['relations_index_url'] = url_for('relations_api.index',
                                              project=self.slug)
        return data
