import logging 

from pprint import pprint
import elasticsearch

from grano.core import es, es_index


log = logging.getLogger(__name__)


class ESSearcher(object):

    def __init__(self, args):
        self.args = args
        self.results = None
        self._limit = 25
        self._offset = 0


    def limit(self, limit):
        self.results = None
        self._limit = limit
        return self

    def offset(self, offset):
        self.results = None
        self._offset = offset
        return self

    @property
    def query_text(self):
        return self.args.get('q', '').strip()

    def _run(self):
        query = {'from': self._offset, 'size': self._limit}
        qt = self.query_text
        if qt is not None and len(qt):
            query["query"] = {
                "query_string": {
                    "query": qt
                }
            }
        else:
            query['query'] = {"match_all": {}}
        self.results = es.search(index=es_index, body=query)

    def __iter__(self):
        if self.results is None:
            self._run()

        for hit in self.results.get('hits').get('hits'):
            yield hit

    def __len__(self):
        if self.results is None:
            self._run()

        return self.results.get('hits').get('total')        

    def count(self):
        return len(self)

    def all(self):
        return list(self)


def search_entities(args):
    return ESSearcher(args)
