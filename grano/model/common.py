import uuid
from datetime import datetime
from slugify import slugify

from grano.core import db


def slugify_column(text):
    return slugify(text).replace('-', '_')


def make_token():
    return uuid.uuid4().get_hex()[15:]


class _CoreBase(object):
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    @classmethod
    def by_id(cls, id):
        q = db.session.query(cls).filter_by(id=id)
        return q.first()

    @classmethod
    def all(cls):
        return db.session.query(cls)


class IntBase(_CoreBase):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.id)


class UUIDBase(_CoreBase):
    id = db.Column(db.Unicode, default=make_token, primary_key=True)

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.id)


class PropertyBase(object):

    @property
    def active_properties(self):
        q = self.properties.filter_by(active=True)
        return q


    @classmethod
    def by_property(cls, name, value, only_active=True):
        from grano.model.property import Property
        q = db.session.query(cls)
        q = q.join(cls.properties)

        q = q.filter(Property.name==name)
        q = q.filter(Property.value==value)
        if only_active:
            q = q.filter(Property.active==True)
            return q.first()
        return q
