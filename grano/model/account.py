from grano.core import db
from grano.model.util import make_token
from grano.model.common import IntBase


class Account(db.Model, IntBase):
    __tablename__ = 'account'

    github_id = db.Column(db.Unicode)
    twitter_id = db.Column(db.Unicode)
    facebook_id = db.Column(db.Unicode)

    full_name = db.Column(db.Unicode)
    login = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    api_key = db.Column(db.Unicode, default=make_token)
    
    projects = db.relationship('Project', backref='author', lazy='dynamic')
    properties = db.relationship('Property', backref='author', lazy='dynamic')
    relations = db.relationship('Relation', backref='author', lazy='dynamic')
    entities = db.relationship('Entity', backref='author', lazy='dynamic')
    
    @property
    def display_name(self):
        if self.full_name is not None and len(self.full_name.strip()):
            return self.full_name
        if self.login is not None and len(self.login.strip()):
            return self.login
        return self.email

    @classmethod
    def by_api_key(cls, api_key):
        q = db.session.query(cls).filter_by(api_key=api_key)
        return q.first()


    @classmethod
    def by_login(cls, login):
        q = db.session.query(cls).filter_by(login=login)
        return q.first()


    @classmethod
    def by_github_id(cls, github_id):
        q = db.session.query(cls).filter_by(github_id=str(github_id))
        return q.first()

    @classmethod
    def by_twitter_id(cls, twitter_id):
        q = db.session.query(cls).filter_by(twitter_id=str(twitter_id))
        return q.first()

    @classmethod
    def by_facebook_id(cls, facebook_id):
        q = db.session.query(cls).filter_by(facebook_id=str(facebook_id))
        return q.first()
