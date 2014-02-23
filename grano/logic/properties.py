from grano.core import db
from grano.model import Entity


def set_many(obj, author, properties):
    """ Set a list of properties supplied as a dictionary containing the 
    arguments necessary for calling set(). """
    
    current_properties = list(obj.properties)
    for name, prop in properties.items():
        relevant = [p for p in current_properties if p.name == name]
        set(obj, author, name, prop.get('schema'), prop.get('value'),
            prop.get('active'), prop.get('source_url'), relevant)


def set(obj, author, name, schema, value, active=True, source_url=None,
    properties=None):
    """ Set a property on the given object (entity or relation). This will
    either create a new property object or re-activate an existing object
    from the same source, if one exists. If the property is defined as 
    ``active``, existing properties with the same name will be de-activated.

    WARNING: This does not, on its own, perform any validation.
    """

    prop = None

    if properties is None:
        # eager loading - change if it's not active any more
        properties = [p for p in obj.properties if p.name == name]

    for cand in properties:
        if cand.value == value:
            prop = cand
        elif cand.active and active:
            cand.active = False

    # TODO: does this cause trouble?
    if value is None:
        return None

    if prop is None:
        prop = obj.PropertyClass()
        db.session.add(prop)

    prop._set_obj(obj)
    prop.name = name
    prop.author = author
    prop.schema = schema
    prop.value = value
    prop.active = active
    prop.source_url = source_url
    return prop


def to_rest_index(prop):
    return prop.name, {
        #'id': prop.id,
        'value': prop.value,
        #'active': prop.active,
        'source_url': prop.source_url
    }

def to_rest(prop):
    name, data = to_rest_index(prop)
    data['id'] = prop.id
    data['active'] = prop.active
    return name, data
