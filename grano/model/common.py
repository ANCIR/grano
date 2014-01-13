import uuid
from datetime import datetime

from grano.core import db


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


class IntBase(object):
    id = db.Column(db.Integer, primary_key=True)


class UUIDBase(object):
    id = db.Column(db.Unicode, default=make_token, primary_key=True)


def make_token():
    return uuid.uuid4().get_hex()[15:]
