from datetime import datetime

from sqlalchemy.orm import aliased

from grano.core import db
from grano.model.common import IntBase
from grano.model.attribute import Attribute

VALUE_COLUMNS = {
    'value_string': basestring,
    'value_datetime': datetime,
    'value_datetime_precision': basestring,
    'value_integer': int,
    'value_float': float,
    'value_boolean': bool
}
DATETIME_PRECISION_ENUM = [
    'year',
    'month',
    'day',
    'hour',
    'minute',
    'second',
    'microsecond'
]


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
    value_datetime_precision = db.Column(db.Enum(*DATETIME_PRECISION_ENUM, native_enum=False))
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

    @classmethod
    def type_column(self, value):
        for name, typ in VALUE_COLUMNS.items():
            if isinstance(value, typ):
                return name
        return 'value_string'

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

    @classmethod
    def _filter_property(cls, q, name, value, only_active=True):
        Prop = aliased(Property)
        q = q.join(Prop, cls.properties)
        q = q.filter(Prop.name == name)
        column = getattr(Prop, Property.type_column(value))
        q = q.filter(column == value)
        if only_active:
            q = q.filter(Prop.active == True) # noqa
        return q
