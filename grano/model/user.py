from flask import url_for
from mongoengine import StringField, EmailField

from grano.model.util import GranoDocument, ObjectExists


class User(GranoDocument):
    email = EmailField(unique=True)
    display_name = StringField(max_length=200)
    browserid_issuer = StringField(max_length=200)

    @property
    def api_uri(self):
        return url_for('users.get', id=self.id, _external=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.is_authenticated()

    def is_anonymous(self):
        return not self.is_authenticated()

    def get_id(self):
        return self.email

    @classmethod
    def by_email(cls, email):
        return cls.objects(email=email).first()

    @classmethod
    def by_id(cls, id_):
        return cls.objects(id=id_).first()

    @classmethod
    def from_browserid(cls, browserid):
        user = cls.objects(email=browserid.get('email'),
                           browserid_issuer=browserid.get('issuer')).first()
        if user is not None:
            return user
        if cls.by_email(browserid.get('email')) is not None:
            raise ObjectExists()
        user = cls(email=browserid.get('email'),
                   browserid_issuer=browserid.get('issuer'))
        user.save()
        return user

    def to_json(self):
        data = super(User, self).to_json()
        data['email'] = self.email
        data['display_name'] = self.display_name
        return data

