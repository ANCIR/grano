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
