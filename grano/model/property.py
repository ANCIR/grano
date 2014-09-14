from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased

from grano.core import db
from grano.model.common import IntBase
from grano.model.attribute import Attribute


class Property(db.Model, IntBase):
    __tablename__ = 'grano_property'

    attribute_id = db.Column(db.Integer, db.ForeignKey('grano_attribute.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))

    entity_id = db.Column(db.Unicode(), db.ForeignKey('grano_entity.id'),
                          index=True, nullable=True)
    relation_id = db.Column(db.Unicode(), db.ForeignKey('grano_relation.id'),
                            index=True, nullable=True)

    name = db.Column(db.Unicode(), index=True)

    value_string = db.Column(db.Unicode())
    value_integer = db.Column(db.Integer())
    value_float = db.Column(db.Float())
    value_datetime = db.Column(db.DateTime())
    value_boolean = db.Column(db.Boolean())
    value_file_id = db.Column(db.Integer(), db.ForeignKey('grano_file.id'))

    source_url = db.Column(db.Unicode())
    active = db.Column(db.Boolean())

    @property
    def value(self):
        # check file column first since file uses both
        # value_string and value_file_id
        if self.value_file_id is not None:
            return self.value_file_id
        for column in Attribute.DATATYPES.values():
            value = getattr(self, column)
            if value is not None:
                return value

    def to_dict_index(self):
        data = {
            'value': self.value,
            'source_url': self.source_url
        }
        if self.value_file_id is not None:
            data['file_url'] = self.value_string
        return data

    def to_dict_kv(self):
        return self.name, self.to_dict_index()

    def to_dict(self):
        name, data = self.to_dict_index()
        data['id'] = self.id
        data['name'] = name
        data['created_at'] = self.created_at
        data['updated_at'] = self.updated_at
        data['active'] = self.active
        return data


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
        Prop = aliased(Property)
        q = q.join(Prop, cls.properties)

        nvs = []
        for attribute in attributes:
            column = getattr(Prop, attribute.value_column)
            nvs.append(and_(Prop.attribute==attribute,
                            column==value))

        q = q.filter(or_(*nvs))
        if only_active:
            q = q.filter(Prop.active==True)
        return q
