from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased

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
        #q = self.properties.filter_by(active=True)
        #q = q.order_by(self.PropertyClass.name.desc())
        q = [p for p in self.properties if p.active]
        return q

    def __getitem__(self, name):
        for prop in self.active_properties:
            if prop.name == name:
                return prop

    def has_property(self, name):
        return self[name] is not None

    def get_attribute(self, prop_name):
        for schema in self.schemata:
            for attribute in schema.attributes:
                if attribute.name == prop_name:
                    return attribute

    def has_schema(self, name):
        for schema in self.schemata:
            if schema.name == name:
                return True
        return False

    @classmethod
    def _filter_property(cls, q, attributes, value, only_active=True):
        # TODO: this is a steaming pile of shit and needs to be fixed 
        # at a fundamental level.

        from grano.model.attribute import Attribute
        Prop = aliased(cls.PropertyClass)
        q = q.join(Prop)
        
        nvs = []
        for attribute in attributes:
            column_name = Attribute.DATATYPES.get(attribute.datatype)
            value_column = getattr(Prop, column_name)
            nvs.append(and_(Prop.attribute==attribute,
                            value_column==value))

        q = q.filter(or_(*nvs))
        if only_active:
            q = q.filter(Prop.active==True)
        
        #q = q.reset_joinpoint()
        return q
