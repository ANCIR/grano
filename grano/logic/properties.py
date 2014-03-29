from datetime import datetime

import colander

from grano.core import db
from grano.logic.validation import FixedValue
from grano.model import Entity, Attribute


DATATYPE_TYPES = {
    'integer': colander.Integer(),
    'float': colander.Float(),
    'boolean': colander.Boolean(),
    'string': colander.String(),
    'datetime': colander.DateTime(default_tzinfo=None)
}


def validate(data, schemata, name='root'):
    """ Compile a validator for the given set of properties, based on
    the available schemata. """
    
    schema = colander.SchemaNode(colander.Mapping(), name=name)
    for sche in schemata:
        for attr in sche.attributes:
            attrib = colander.SchemaNode(colander.Mapping(),
                name=attr.name, missing=colander.null)

            if attr.name == 'name':
                attrib.add(colander.SchemaNode(colander.String(),
                    missing=colander.required,
                    validator=colander.Length(min=1),
                    name='value'))
            else:
                T = DATATYPE_TYPES.get(attr.datatype)
                attrib.add(colander.SchemaNode(T, missing=None, name='value'))
            
            attrib.add(colander.SchemaNode(colander.Boolean(),
                default=True, missing=True, name='active'))
            attrib.add(colander.SchemaNode(FixedValue(sche), name='schema'))
            attrib.add(colander.SchemaNode(FixedValue(attr), name='attribute'))

            attrib.add(colander.SchemaNode(colander.String(),
                missing=None, name='source_url'))

            schema.add(attrib)

    data = schema.deserialize(data)
    out = {}
    for k, v in data.items():
        if v != colander.null:
            out[k] = v
    return out


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


def delete(prop):
    """ Delete a property. """
    db.session.delete(prop)


def to_rest_index(prop):
    value = prop.value
    return prop.name, {
        'value': value,
        'source_url': prop.source_url
    }


def to_rest(prop):
    name, data = to_rest_index(prop)
    data['id'] = prop.id
    data['active'] = prop.active
    return name, data
