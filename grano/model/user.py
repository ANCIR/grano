from flask import url_for
from datetime import datetime

#from formencode import Schema, validators
from grano.core import mongo
from grano.model.util import ObjectExists


def find_by_email(email):
    return mongo.db.user.find_one({'email': email})


def login_by_email(email):
    user = find_by_email(email)
    if user is None:
        return None
    return LoginUser(user)


def login_by_browserid(browserid):
    user = mongo.db.user.find_one({
        'browserid.email': browserid.get('email'),
        'browserid.issuer': browserid.get('issuer')
    })
    if user is None:
        user = create(browserid.get('email'),
                      {'browserid': browserid})
    return LoginUser(user)


def create(email, data=None):
    obj = find_by_email(email)
    if obj is not None:
        raise ObjectExists()
    data = data or {}
    data.update({
        'email': email,
        'display_name': '',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    })
    data['_id'] = mongo.db.user.insert(data)
    return data


class LoginUser(object):

    def __init__(self, user):
        self.user = user

    def is_authenticated(self):
        return self.user is not None

    def is_active(self):
        return self.is_authenticated()

    def is_anonymous(self):
        return not self.is_authenticated()

    def get_id(self):
        return self.user.get('email')

