from grano.core import db
from grano.model.common import UUIDBase, PropertyBase

from grano.model.schema import Schema
from grano.model.relation import Relation
from grano.model.property import EntityProperty


entity_schema = db.Table('entity_schema',
    db.Column('entity_id', db.Unicode, db.ForeignKey('entity.id')),
    db.Column('schema_id', db.Integer, db.ForeignKey('schema.id'))
)


class Entity(db.Model, UUIDBase, PropertyBase):
    OBJ = __tablename__ = 'entity'
    PROPERTIES = EntityProperty

    schemata = db.relationship('Schema', secondary=entity_schema,
        backref=db.backref('entities', lazy='dynamic'))
    
    inbound = db.relationship('Relation', lazy='dynamic', backref='target',
        primaryjoin='Entity.id==Relation.target_id')
    outbound = db.relationship('Relation', lazy='dynamic', backref='source',
        primaryjoin='Entity.id==Relation.source_id')

    properties = db.relationship(EntityProperty, backref='entity',
        order_by=EntityProperty.created_at.desc(),
        lazy='dynamic')


    @classmethod
    def by_name(cls, name, only_active=False):
        q = db.session.query(cls)
        q = cls._filter_property(q, 'name', name, only_active=only_active)
        return q.first()

    @classmethod
    def save(cls, schemata, properties, update_criteria):
        obj = None
        if len(update_criteria):
            q = db.session.query(cls)
            for name, only_active in update_criteria:
                value = properties.get(name).get('value')
                q = cls._filter_property(q, name, value, only_active=only_active)
            obj = q.first()
        if obj is None:
            obj = cls()
            db.session.add(obj)
        obj.schemata = list(set(obj.schemata + schemata))
        obj._update_properties(properties)
        return obj

    def merge_into(self, target):
        target_active = [p.name for p in target.active_properties]
        target.schemata = list(set(target.schemata + self.schemata))
        for prop in self.properties:
            if prop.name in target_active:
                prop.active = False
            prop.entity = target
        for rel in self.inbound:
            # TODO: what if this relation now points at the same thing on both ends?
            rel.target = target
        for rel in self.outbound:
            rel.source = target
        # Authorization code RIKER B4921A
        db.session.delete(self)

    @property
    def inbound_schemata(self):
        from grano.model.relation import Relation
        q = db.session.query(Schema)
        q = q.join(Schema.relations)
        q = q.filter(Relation.target_id==self.id)
        return q.distinct()

    def inbound_by_schema(self, schema):
        q = self.inbound.filter_by(schema=schema)
        return q

    @property
    def outbound_schemata(self):
        from grano.model.relation import Relation
        q = db.session.query(Schema)
        q = q.join(Schema.relations)
        q = q.filter(Relation.source_id==self.id)
        return q.distinct()

    def outbound_by_schema(self, schema):
        q = self.outbound.filter_by(schema=schema)
        return q

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

    def to_basic_dict(self):
        data = {}
        for prop in self.active_properties:
            data[prop.name] = prop.value
        return {
            'id': self.id,
            'schemata': [s.name for s in self.schemata],
            'properties': data
        }

    def to_index(self):
        data = {
            'id': self.id,
            'schemata': [s.to_dict(shallow=True) for s in self.schemata if s.name != 'base'],
            'num_schemata': len(self.schemata),
            'num_properties': 0,
            'inbound': [],
            'outbound': [],
            'relations': [],
            'names': []
            }

        # TODO: relations
        for rel in self.inbound:
            rel_data = rel.to_index()
            data['inbound'].append(rel_data)
            data['relations'].append(rel_data)

        for rel in self.outbound:
            rel_data = rel.to_index()
            data['outbound'].append(rel_data)
            data['relations'].append(rel_data)

        data['num_relations'] = len(data['relations'])

        for prop in self.properties:
            if prop.name == 'name':
                data['names'].append(prop.value)
            if prop.active and prop.qualified_name not in data:
                data[prop.qualified_name] = prop.value
                data['num_properties'] += 1

        return data
