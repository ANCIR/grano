import logging
from unicodecsv import DictReader, DictWriter
from sqlalchemy.orm import aliased

from grano.core import db
from grano.logic import entities
from grano.model import Entity, EntityProperty, Schema

log = logging.getLogger(__name__)


## Import commands
def import_aliases(project, author, path):
    """ Import aliases from a CSV file. This will not create new entities, but
    re-name existing entities or merge two entities if one's name is given as 
    an alias for the other. """
    with open(path, 'r') as fh:
        reader = DictReader(fh)
        for i, row in enumerate(reader):
            data = {}
            for k, v in row.items():
                k = k.lower().strip()
                data[k] = v
            assert 'canonical' in data, 'No "canonical" column!'
            assert 'alias' in data, 'No "alias" column!'
            entities.apply_alias(project, author,
                data.get('canonical'),
                data.get('alias'))
            if i % 1000 == 0:
                db.session.commit()
        db.session.commit()


## Export commands
def export_aliases(project, path):
    """ Dump a list of all entity names to a CSV file. The table will contain the 
    active name of each entity, and one of the other existing names as an alias. """
    with open(path, 'w') as fh:
        writer = DictWriter(fh, ['entity_id', 'alias', 'canonical'])
        writer.writeheader()

        alias = aliased(EntityProperty)
        canonical = aliased(EntityProperty)
        q = db.session.query(alias.value_string.label('alias'), alias.entity_id)
        q = q.join(Entity)
        q = q.join(canonical)
        q = q.filter(Entity.project_id==project.id)
        q = q.filter(alias.entity_id!=None)
        q = q.filter(alias.name=='name')
        q = q.filter(canonical.name=='name')
        q = q.filter(canonical.active==True)
        q = q.add_columns(canonical.value_string.label('canonical'))
        for row in q.all():
            #if row.alias == row.canonical:
            #    continue
            writer.writerow({
                'entity_id': str(row.entity_id),
                'alias': row.alias,
                'canonical': row.canonical
            })
        
