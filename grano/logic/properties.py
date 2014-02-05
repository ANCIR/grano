from grano.core import db
from grano.model import Entity
from grano.logic.validation import validate_properties


def set_many(obj, properties):
    """ Set a list of properties supplied as a dictionary containing the 
    arguments necessary for calling set(). """
    
    properties = validate_properties(properties, obj.schemata)

    current_properties = list(obj.properties)
    for name, prop in properties.items():
        relevant = [p for p in current_properties if p.name == name]
        set(obj, name, prop.get('schema'), prop.get('value'),
            prop.get('active'), prop.get('source_url'), relevant)


def set(obj, name, schema, value, active=True, source_url=None,
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
        if cand.source_url == source_url and cand.value == value:
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
    prop.schema = schema
    prop.value = value
    prop.active = active
    prop.source_url = source_url
    return prop
