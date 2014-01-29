from grano.core import db
from grano.model.common import UUIDBase, PropertyBase
from grano.model.property import RelationProperty


class Relation(db.Model, UUIDBase, PropertyBase):
    __tablename__ = 'relation'
    PropertyClass = RelationProperty

    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'), index=True)
    source_id = db.Column(db.Unicode, db.ForeignKey('entity.id'), index=True)
    target_id = db.Column(db.Unicode, db.ForeignKey('entity.id'), index=True)

    properties = db.relationship(RelationProperty,
    	order_by=RelationProperty.created_at.desc(),
    	backref='relation', lazy='dynamic')


    def get_attribute(self, prop_name):
        for attribute in self.schema.attributes:
            if attribute.name == prop_name:
                return attribute


    @classmethod
    def save(cls, schema, properties, source, target, update_criteria):
    	q = db.session.query(cls)
    	q = q.filter(cls.source_id==source.id)
    	q = q.filter(cls.target_id==target.id)
    	for name, only_active in update_criteria:
    		value = properties.get(name).get('value')
    		q = cls._filter_property(q, name, value, only_active=only_active)
    	obj = q.first()
    	if obj is None:
        	obj = cls()
        	db.session.add(obj)
        obj.source = source
        obj.target = target
        obj.schema = schema
        obj._update_properties(properties)
        return obj


    def to_index(self):
        data = {
            'id': self.id,
            'source': self.source_id,
            'target': self.target_id,
            'schema': self.schema.to_dict(shallow=True),
        }        
        for prop in self.active_properties:
            data[prop.qualified_name] = prop.value
        return data
