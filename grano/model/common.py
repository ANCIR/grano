from datetime import datetime

from grano.core import db
from grano.model.util import make_token


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
        q = q.order_by(self.PropertyClass.name.desc())
        return q

    def __getitem__(self, name):
        for prop in self.active_properties:
            if prop.name == name:
                return prop

    def has_property(self, name):
        return self[name] is not None

    @classmethod
    def _filter_property(cls, q, name, value, only_active=True):
        # TODO: move to logic layer?
        q = q.join(cls.properties, aliased=True)
        q = q.filter(cls.PropertyClass.name==name)
        q = q.filter(cls.PropertyClass.value==value)
        if only_active:
            q = q.filter(cls.PropertyClass.active==True)
        q = q.reset_joinpoint()
        return q


    @classmethod
    def by_property(cls, name, value, only_active=True):
        q = db.session.query(cls)
        q = cls._filter_property(q, name, value, only_active=only_active)
        return q
