import logging 
from pprint import pprint

from grano.core import es, es_index
from grano.model import Entity
from grano.logic import entities
from grano.interface import EntityChangeProcessor


log = logging.getLogger(__name__)


def index_entities():
    """ Re-build an index for all enitites from scratch. """
    for i, entity in enumerate(Entity.all().filter_by(same_as=None)):
        body = entities.to_index(entity)
        
        if not 'name' in body:
            log.warn('No name: %s, skipping!', entity.id)
            continue
    
        es.index(index=es_index, doc_type='entity', id=body.pop('id'), body=body)
        if i > 0 and i % 1000 == 0:
            log.info("Indexed: %s entities", i)
            es.indices.refresh(index=es_index)
        
    es.indices.refresh(index=es_index)


def index_single(entity_id):
    """ Index a single entity. """
    entity = Entity.by_id(entity_id)
    body = entities.to_index(entity)
    es.index(index=es_index, doc_type='entity', id=body.pop('id'), body=body)
    es.indices.refresh(index=es_index)


def flush_entities():
    """ Delete the entire index. """
    query = {'query': {"match_all": {}}}
    es.delete_by_query(index=es_index, doc_type='entity', q='*:*')


class AutoIndexer(EntityChangeProcessor):

    def entity_changed(self, entity_id):
        index_single(entity_id)
