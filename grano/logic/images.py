import os
import mimetypes
from StringIO import StringIO

import colander
from PIL import Image

from grano.core import db
from grano.logic import files as files_logic
from grano.model import Attribute, Property, File, ImageConfig
from grano.logic.references import ProjectRef


ACCEPTED_EXTENSIONS = set(('.png', '.jpg', '.jpeg', '.bmp'))
ACCEPTED_MIMETYPES = set()
for ext in ACCEPTED_EXTENSIONS:
    ACCEPTED_MIMETYPES.add(mimetypes.types_map[ext])
    if ext in mimetypes.common_types:
        ACCEPTED_MIMETYPES.add(mimetypes.common_types[ext])


class ImageConfigValidator(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    label = colander.SchemaNode(colander.String(),
            missing='', default='')
    description = colander.SchemaNode(colander.String(),
            missing='', default='')
    project = colander.SchemaNode(ProjectRef())
    height = colander.SchemaNode(colander.Integer(),
            validator=colander.Range(min=1))
    width = colander.SchemaNode(colander.Integer(),
            validator=colander.Range(min=1))


def validate_imageconfig(data):
    validator = ImageConfigValidator()
    sane = validator.deserialize(data)
    return sane


def save_imageconfig(data):
    data = validate_imageconfig(data)

    project = data.get('project')
    name = data.get('name')
    obj = ImageConfig.by_project_and_name(project, name)
    if obj is None:
        obj = ImageConfig()
        obj.name = name
        obj.project = project
        db.session.add(obj)

    obj.label = data.get('label')
    obj.description = data.get('description')
    old_height = obj.height
    old_width = obj.width
    obj.height = data.get('height')
    obj.width = data.get('width')
    if obj.height != old_height or obj.width != old_width:
        db.session.flush()
        update_by_imageconfig(obj.id)

    return obj


def validate(file):
    """ Simply checks that we accept the file mimetype """
    if file.mime_type not in ACCEPTED_MIMETYPES:
        raise ValueError("Invalid image MIME type '%s'" % file.mime_type)


def transform(file):
    sio = StringIO(file.data)
    image = Image.open(sio)
    image.load()
    sio.close()
    if file.image_config is not None:
        config = file.image_config
        # crop and scale ourselves since Image.thumbnail
        # doesn't change the aspect ratio
        crop_box = config.crop_box(image.size)
        image = image.crop(crop_box)
        image = image.resize((config.width, config.height), Image.ANTIALIAS)
    out = StringIO()
    image.save(out, 'PNG')
    return out


# TODO: convert to celery task
def update_by_attribute(attr_id):
    attr = db.session.query(Attribute).get(attr_id)
    q = attr.properties.filter(Property.value_file_id != None)
    q = q.values(Property.value_file_id)
    for file_id, in q:
        update(file_id, attr.image_config_id)


# TODO: convert to celery task
def update_by_imageconfig(imageconfig_id):
    config = db.session.query(ImageConfig).get(imageconfig_id)
    q = config.files.values(File.id)
    for file_id, in q:
        update(file_id, config.id)


# TODO: convert to celery task
def update(file_id, image_config_id=None):
    file = db.session.query(File).get(file_id)
    if image_config_id is not None:
        file.image_config_id = image_config_id
    try:
        validate(file)
    except ValueError:
        return

    new_file = transform(file)
    url = make_url(file)
    files_logic.upload(new_file, url)
    new_file.close()
    file.properties.update({'value_string': url})
    db.session.commit()


def make_url(file):
    # TODO: base URL on some image upload setting
    return 'file://%s' % os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../../images',
        '%s-%s-%s.png' % (
            os.path.splitext(os.path.basename(file.file_name))[0],
            file.id,
            file.image_config_id or 0
        )
    ))
