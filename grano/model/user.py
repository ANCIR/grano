from flask import url_for

#from formencode import Schema, validators

from grano.core import db
from grano.model.util import ModelCore, make_token


#class UserSchema(Schema):
#    allow_extra_fields = True
#    name = validators.String(min=3, max=255)
#    email = validators.Email()


class User(db.Model, ModelCore):
    __tablename__ = 'user'

    screen_name = db.Column(db.Unicode())
    name = db.Column(db.Unicode())
    email = db.Column(db.Unicode())
    twitter_id = db.Column(db.Unicode())
    facebook_id = db.Column(db.Unicode())
    api_key = db.Column(db.Unicode(), default=make_token)

    @classmethod
    def create(cls, data):
        obj = cls()
        obj.screen_name = data.get('screen_name')
        obj.name = data.get('name')
        obj.twitter_id = data.get('twitter_id')
        obj.facebook_id = data.get('facebook_id')
        db.session.add(obj)
        return obj

    def update(self, data):
        #data = UserSchema().to_python(data)
        self.name = data['name']
        self.email = data['email']
        db.session.add(self)

    @classmethod
    def by_screen_name(cls, screen_name):
        q = db.session.query(cls)
        q = q.filter_by(screen_name=screen_name)
        return q.first()

    @classmethod
    def by_api_key(cls, api_key):
        q = db.session.query(cls).filter_by(api_key=api_key)
        return q.first()

    @classmethod
    def by_twitter_id(cls, twitter_id):
        q = db.session.query(cls).filter_by(twitter_id=twitter_id)
        return q.first()

    @classmethod
    def by_facebook_id(cls, facebook_id):
        q = db.session.query(cls).filter_by(facebook_id=facebook_id)
        return q.first()

    def to_ref(self):
        return {
            'id': self.id,
            'screen_name': self.screen_name,
        #    'uri': url_for('users.get', id=self.id, _external=True),
            'name': self.name
        }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'created_at': self.created_at,
            'updated_at': self.updated_at
        })
        return data
