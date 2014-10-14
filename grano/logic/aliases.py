import os
import logging
from unicodecsv import DictReader, DictWriter
from sqlalchemy.orm import aliased

from grano.core import db
from grano.logic import entities, pipelines, imports
from grano.model import Entity, Property, Schema

log = logging.getLogger(__name__)


## Import commands
def import_aliases(project, author, path):
    """ Set up a data pipeline and execute it. """
    with open(path, 'r') as fh:
        config = {'mapping': {
            'canonical': {'attribute': 'canonical'},
            'alias': {'attribute': 'alias'}
        }}
        name = os.path.basename(path)
        pipeline = pipelines.create(project, 'import',
                                    name, config, author)
        pipelines.start(pipeline)
        imports.import_aliases(pipeline, fh)
        pipelines.finish(pipeline)


## Export commands
def export_aliases(project, fh):
    """ Dump a list of all entity names to a CSV file. The table will contain
    the active name of each entity, and one of the other existing names as an
    alias. """

    writer = DictWriter(fh, ['entity_id', 'schema', 'alias', 'canonical'])
    writer.writeheader()

    alias = aliased(Property)
    canonical = aliased(Property)
    schema = aliased(Schema)
    q = db.session.query(alias.value_string.label('alias'), alias.entity_id)
    q = q.join(Entity)
    q = q.join(schema)
    q = q.join(canonical)
    q = q.filter(Entity.project_id == project.id)
    q = q.filter(alias.entity_id != None) # noqa
    q = q.filter(alias.name == 'name')
    q = q.filter(canonical.name == 'name')
    q = q.filter(canonical.active == True) # noqa
    q = q.add_columns(canonical.value_string.label('canonical'))
    q = q.add_columns(schema.name.label('schema'))
    for row in q.all():
        writer.writerow({
            'entity_id': str(row.entity_id),
            'schema': row.schema,
            'alias': row.alias,
            'canonical': row.canonical
        })
