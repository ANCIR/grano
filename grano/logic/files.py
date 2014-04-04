from StringIO import StringIO
from unicodecsv import DictReader, DictWriter
from unicodecsv import Error as CSVError
import logging
import colander

from grano.core import db, url_for, celery
from grano.model import File
from grano.logic import projects as projects_logic
from grano.logic.references import ProjectRef, AccountRef
from grano.plugins import notify_plugins
from grano.lib.exc import BadRequest


log = logging.getLogger(__name__)


class FileValidator(colander.MappingSchema):
    author = colander.SchemaNode(AccountRef())
    project = colander.SchemaNode(ProjectRef())
    file_name = colander.SchemaNode(colander.String(),
            validator=colander.Length(min=3))
    mime_type = colander.SchemaNode(colander.String(),
            validator=colander.Length(min=3))


def validate(data, file):
    validator = FileValidator()
    sane = validator.deserialize(data)
    return sane


def save(data, file_data, file=None):
    """ Save or update a file. """
    if file_data is None:
        raise BadRequest("No file given!")
    
    data.update({
        'file_name': file_data.filename,
        'mime_type': file_data.mimetype
        })
    sane = validate(data, file)
    
    if file is None:
        file = File()
        file.project = sane.get('project')
        file.author = sane.get('author')
        db.session.add(file)

    file.file_name = sane.get('file_name')
    file.mime_type = sane.get('mime_type')
    file.data = file_data.read()

    db.session.flush()
    return file


def delete(file):
    """ Delete the file. """
    db.session.delete(file)


def as_table(file, limit=None):
    try:
        sio = StringIO(file.data)
        reader = DictReader(sio)
        data = {'headers': None, 'rows': [], 'total': 0}
        for i, row in enumerate(reader):
            if data['headers'] is None:
                data['headers'] = row.keys()
            if limit is None or i < limit:
                rd = [row.get(k) for k in data['headers']]
                data['rows'].append(rd)
            data['total'] = i
        return data
    except CSVError, e:
        return {'status': 'error', 'error': unicode(e)}
