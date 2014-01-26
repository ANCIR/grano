import logging
from unicodecsv import DictReader, DictWriter

from grano.core import db
from grano.model import Entity, Schema

log = logging.getLogger(__name__)

## Import commands

def import_aliases(path):
    with open(path, 'r') as fh:
        reader = DictReader(fh)
        for i, row in enumerate(reader):
            data = {}
            for k, v in row.items():
                k = k.lower().strip()
                data[k] = v
            assert 'canonical' in data, 'No "canonical" column!'
            assert 'alias' in data, 'No "alias" column!'
            import_alias(data)
            if i % 1000 == 0:
                db.session.commit()
        db.session.commit()


def import_alias(data):
    # TODO: this actually deleted old entities, i.e. makes invalid 
    # entities - we should try and either re-direct them, or keep 
    # old entities whenever that makes sense.
    canonical_name = data.get('canonical').strip()
    alias_name = data.get('alias')

    if canonical_name == alias_name or not len(canonical_name):
        log.info("SKIP: %s", canonical_name)
        return

    canonical = Entity.by_name(canonical_name)
    alias = Entity.by_name(alias_name)
    schema = Schema.cached(Entity, 'base')

    if canonical is None:
        if alias is None:
            prop = {
                'value': canonical_name,
                'active': True,
                'schema': schema,
                'source_url': data.get('source_url')
                }
            canonical = Entity.save([schema], {'name': prop}, [])
            db.session.flush()
            canonical.create_property('name', schema, alias_name,
                active=False, source_url=data.get('source_url'))
            log.info("Aliased.")
            return
        else:
            alias.create_property('name', schema, canonical_name,
                active=True, source_url=data.get('source_url'))
            log.info("Renamed.")
            return
    if canonical is not None and alias is not None:
        if canonical != alias:
            alias.merge_into(canonical)
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


