import logging 

from pprint import pprint
import elasticsearch

from grano.core import es, es_index
from grano.model import Entity
from grano.logic import entities


log = logging.getLogger(__name__)


def index_entities():
    """ Re-build an index for all enitites from scratch. """
    for i, entity in enumerate(Entity.all().filter_by(same_as=None).yield_per(1000)):
        body = entities.to_index(entity)
        es.index(index=es_index, doc_type='entity', id=body.pop('id'), body=body)
        #log.info('Indexing: %s', body.get('name'))
        if i % 100 == 0:
            log.info("Indexed: %s entities", i)
    es.indices.refresh(index=es_index)


def flush_entities():
    """ Delete the entire index. """
    query = {'query': {"match_all": {}}}
    es.delete_by_query(index=es_index, doc_type='entity', q='*:*')
