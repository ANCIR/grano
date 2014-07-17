import os
import mimetypes
from StringIO import StringIO

from PIL import Image

from grano.core import db
from grano.logic import files as files_logic
from grano.model import Attribute, Property, File


ACCEPTED_EXTENSIONS = set(('.png', '.jpg', '.jpeg', '.bmp'))
ACCEPTED_MIMETYPES = set()
for ext in ACCEPTED_EXTENSIONS:
    ACCEPTED_MIMETYPES.add(mimetypes.types_map[ext])
    if ext in mimetypes.common_types:
        ACCEPTED_MIMETYPES.add(mimetypes.common_types[ext])


def validate(file):
    """ Simply checks that we accept the file mimetype """
    if file.mime_type not in ACCEPTED_MIMETYPES:
        raise ValueError("Invalid image MIME type '%s'" % file.mime_type)


def transform(file):
    image = Image.open(StringIO(file.data))
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
    q = attr.properties.filter_by(active=True)
    q = q.values(Property.value_file_id)
    for file_id, in q:
        update(file_id, attr.image_config_id)


# TODO: convert to celery task
def update(file_id, image_config_id=None):
    if image_config_id is not None:
        file = db.session.query(File).get(file_id)
        file.image_config_id = image_config_id
        db.session.commit()
    try:
        validate(file)
    except ValueError:
        return

    new_file = transform(file)
    url = make_url(file)
    # TODO: cleanup old files?
    files_logic.upload_file(file, new_file, url)


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
