from grano.core import db
from grano.model.util import make_token
from grano.model.common import IntBase


class Account(db.Model, IntBase):
    __tablename__ = 'account'

    github_id = db.Column(db.Integer)
    login = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    api_key = db.Column(db.Unicode, default=make_token)
    
    projects = db.relationship('Project', backref='owner', lazy='dynamic')
    properties = db.relationship('Property', backref='author', lazy='dynamic')
    relations = db.relationship('Relation', backref='author', lazy='dynamic')
    entities = db.relationship('Entity', backref='author', lazy='dynamic')
    

    @classmethod
    def by_api_key(cls, api_key):
        q = db.session.query(cls).filter_by(api_key=api_key)
        return q.first()


    @classmethod
    def by_github_id(cls, github_id):
        q = db.session.query(cls).filter_by(github_id=github_id)
        return q.first()
