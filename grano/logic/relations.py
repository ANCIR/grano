from grano.core import db
from grano.model import Relation
from grano.logic import properties as properties_logic


def save(schema, properties, source, target, update_criteria):
    """ Save or update a relation with the given properties. """

    q = db.session.query(Relation)
    q = q.filter(Relation.source_id==source.id)
    q = q.filter(Relation.target_id==target.id)
    for name, only_active in update_criteria:
        value = properties.get(name).get('value')
        q = Relation._filter_property(q, name, value, only_active=only_active)
    obj = q.first()

    if obj is None:
        obj = Relation()
        db.session.add(obj)
    
    obj.source = source
    obj.target = target
    obj.schema = schema
    properties_logic.set_many(obj, properties)
    return obj


def to_index(relation):
    """ Convert a relation into a form appropriate for indexing within an 
    entity (ie. do not include entity data). """

    data = {
        'id': relation.id,
        'source': relation.source_id,
        'target': relation.target_id,
        'schema': relation.schema.to_dict(shallow=True),
    }

    for prop in relation.active_properties:
        data[prop.name] = prop.value

    return data
