import logging
from unicodecsv import DictReader, DictWriter

from grano.core import db
from grano.model import Entity, Schema

log = logging.getLogger(__name__)

## Import commands

def import_aliases(path):
    with open(path, 'r') as fh:
        reader = DictReader(fh)
        for row in reader:
            data = {}
            for k, v in row.items():
                k = k.lower().strip()
                data[k] = v
            assert 'canonical' in data, 'No "canonical" column!'
            assert 'alias' in data, 'No "alias" column!'
            import_alias(data)
        db.session.commit()


def import_alias(data):
    # TODO: this actually deleted old entities, i.e. makes invalid 
    # entities - we should try and either re-direct them, or keep 
    # old entities whenever that makes sense.
    canonical = Entity.by_name(data.get('canonical'))
    if canonical is None:
        schema = Schema.cached('entity', 'base')
        prop = {
            'name': 'name', 
            'value': data.get('canonical'),
            'active': True,
            'schema': schema,
            'source_url': data.get('source_url')
            }
        canonical = Entity.save([schema], [prop], [])
        db.session.flush()

    alias = Entity.by_name(data.get('alias'))
    if alias is None:
        Entity.PROPERTIES.save(canonical, 'name', {
            'schema': Schema.cached('entity', 'base'),
            'value': data.get('alias'),
            'active': False,
            'source_url': data.get('source_url')
            })

    elif alias.id != canonical.id:
        alias.merge_into(canonical)

    if alias.id != canonical.id:
        log.info("Mapped: %s -> %s", alias.id, canonical.id)


## Export commands

def export_aliases(path):
    with open(path, 'w') as fh:
        writer = DictWriter(fh, ['entity_id', 'alias', 'canonical'])
        writer.writeheader()
        for entity in Entity.all():
            #print entity
            export_entity(entity, writer)


def export_entity(entity, writer):
    canonical = None
    aliases = []
    for prop in entity.properties.filter_by(name='name'):
        aliases.append(prop.value)
        if prop.active:
            canonical = prop.value
    for alias in aliases:
        writer.writerow({
            'entity_id': entity.id,
            'alias': alias,
            'canonical': canonical
            })


