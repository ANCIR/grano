import logging
from unicodecsv import DictReader, DictWriter

from grano.core import db
from grano.logic import entities
from grano.model import Entity, Schema

log = logging.getLogger(__name__)


## Import commands

def import_aliases(path):
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
            entities.apply_alias(data.get('canonical'), data.get('alias'))
            if i % 1000 == 0:
                db.session.commit()
        db.session.commit()


## Export commands

def export_aliases(path):
    """ Dump a list of all entity names to a CSV file. The table will contain the 
    active name of each entity, and one of the other existing names as an alias. """
    with open(path, 'w') as fh:
        writer = DictWriter(fh, ['entity_id', 'alias', 'canonical', 'schemata'])
        writer.writeheader()
        for i, entity in enumerate(Entity.all().filter_by(same_as=None)):
            export_entity(entity, writer)
            if i % 100 == 0:
                log.info("Dumped %s entity names...", i)


def export_entity(entity, writer):
    canonical = None
    aliases = []
    schemata = ':'.join([s.name for s in entity.schemata])
    schemata = ":%s:" % schemata
    for prop in entity.properties.filter_by(name='name'):
        aliases.append(prop.value)
        if prop.active:
            canonical = prop.value
    for alias in aliases:
        writer.writerow({
            'entity_id': entity.id,
            'alias': alias,
            'canonical': canonical,
            'schemata': schemata
            })


