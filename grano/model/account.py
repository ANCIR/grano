from grano.core import db
from grano.model.util import make_token
from grano.model.common import IntBase


class Account(db.Model, IntBase):
    __tablename__ = 'account'

    github_id = db.Column(db.Integer)
    login = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    api_key = db.Column(db.Unicode, default=make_token)
    
    #datasets = db.relationship('Dataset', backref='owner',
    #                           lazy='dynamic')
    #uploads = db.relationship('Upload', backref='creator',
    #                           lazy='dynamic')
    #entities_created = db.relationship('Entity', backref='creator',
    #                           lazy='dynamic')


    @classmethod
    def by_api_key(cls, api_key):
        q = db.session.query(cls).filter_by(api_key=api_key)
        return q.first()


    @classmethod
    def by_github_id(cls, github_id):
        q = db.session.query(cls).filter_by(github_id=github_id)
        return q.first()
