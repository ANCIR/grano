from datetime import datetime

from grano.core import db
from grano.model import Entity, Attribute


def save(obj, data):
    """ Set a property on the given object (entity or relation). This will
    either create a new property object or re-activate an existing object
    from the same source, if one exists. If the property is defined as 
    ``active``, existing properties with the same name will be de-activated.

    WARNING: This does not, on its own, perform any validation.
    """
    prop = None
    
    for cand in obj.properties:
        if cand.name != data.get('name'):
            continue
        if cand.value == data.get('value'):
            prop = cand
        elif cand.active and data.get('active'):
            cand.active = False

    if prop is None:
        prop = obj.PropertyClass()
        db.session.add(prop)

    prop._set_obj(obj)
    
    setattr(prop, data.get('attribute').value_column,
        data.get('value'))

    prop.name = data.get('name')
    prop.author = data.get('author')
    prop.schema = data.get('schema')
    prop.attribute = data.get('attribute')
    prop.active = data.get('active')
    prop.source_url = data.get('source_url')
    prop.updated_at = datetime.utcnow()
    obj.updated_at = datetime.utcnow()
    return prop


def to_rest_index(prop):
    value = prop.value
    if isinstance(value, datetime):
        value = value.isoformat()
    return prop.name, {
        #'id': prop.id,
        'value': value,
        #'active': prop.active,
        'source_url': prop.source_url
    }


def to_rest(prop):
    name, data = to_rest_index(prop)
    data['id'] = prop.id
    data['active'] = prop.active
    return name, data
