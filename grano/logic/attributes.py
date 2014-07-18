from sqlalchemy.orm.exc import NoResultFound

from grano.core import db
from grano.logic import images as images_logic
from grano.model import Attribute, Property, ImageConfig


def save(data):
    """ Create or update an attribute. 
    CAUTION: This does not, on its own, validate any data."""

    schema = data.get('schema')
    name = data.get('name')
    obj = Attribute.by_schema_and_name(schema, name)
    if obj is None:
        obj = Attribute()
        obj.name = name
        obj.datatype = data.get('datatype')
        obj.schema = schema

    obj.label = data.get('label')
    obj.hidden = data.get('hidden')
    obj.description = data.get('description')
    db.session.add(obj)

    if obj.datatype == 'file' and 'image_config' in data:
        try:
            image_config = ImageConfig.by_project_and_name(
                project=obj.schema.project,
                name=data.get('image_config')
            )
            if obj.image_config != image_config:
                obj.image_config = image_config
                db.session.flush()
                images_logic.update_by_attribute(obj.id)
        except NoResultFound:
            raise ValueError("Image config with name '%s' does not exist"
                             % data.get('image_config'))

    return obj


def delete(attribute):
    """ Delete the attribute and all related properties. """
    q = db.session.query(Property)
    q = q.filter(Property.attribute==attribute)
    q.delete()
    db.session.delete(attribute)
