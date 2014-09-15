from grano.core import db, url_for
from grano.model.common import UUIDBase
from grano.model.property import Property, PropertyBase


class Relation(db.Model, UUIDBase, PropertyBase):
    __tablename__ = 'grano_relation'
    #PropertyClass = RelationProperty

    schema_id = db.Column(db.Integer, db.ForeignKey('grano_schema.id'), index=True)
    source_id = db.Column(db.Unicode, db.ForeignKey('grano_entity.id'), index=True)
    target_id = db.Column(db.Unicode, db.ForeignKey('grano_entity.id'), index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('grano_project.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))

    properties = db.relationship(Property,
                                 order_by=Property.created_at.desc(),
                                 cascade='all, delete, delete-orphan',                                 
                                 backref='relation', lazy='dynamic')

    @property
    def schemata(self):
        return [self.schema]

    def to_dict_base(self):
        return {
            'id': self.id,
            'properties': {},
            'project': self.project.to_dict_index(),
            'api_url': url_for('relations_api.view', id=self.id),
            'schema': self.schema.to_dict_index(),
            'source': self.source.to_dict_index(),
            'target': self.target.to_dict_index()
        }

    def to_dict(self):
        data = self.to_dict_base()
        for prop in self.active_properties:
            name, prop = prop.to_dict_kv()
            data['properties'][name] = prop
        return data

    def to_dict_index(self):
        data = self.to_dict_base()
        for prop in self.active_properties:
            name, prop = prop.to_dict_kv()
            data['properties'][name] = prop
        return data


class BidiRelation(db.Model):
    __tablename__ = 'grano_relation_bidi'

    id = db.Column(db.Unicode, primary_key=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    reverse = db.Column(db.Boolean)
    
    relation_id = db.Column(db.Unicode)
    source_id = db.Column(db.Unicode)
    target_id = db.Column(db.Unicode)
    project_id = db.Column(db.Integer)
    schema_id = db.Column(db.Integer)
    author_id = db.Column(db.Integer)
