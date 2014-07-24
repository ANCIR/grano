from grano.core import db
from grano.model.common import IntBase
from grano.model.attribute import Attribute


class Property(db.Model, IntBase):
    __tablename__ = 'grano_property'

    schema_id = db.Column(db.Integer, db.ForeignKey('grano_schema.id'))
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
