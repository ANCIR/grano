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
        self._facets = []

    def limit(self, limit):
        self.results = None
        self._limit = limit
        return self

    def offset(self, offset):
        self.results = None
        self._offset = offset
        return self

    def add_facet(self, name, size=10):
        self._facets.append((name, size))

    @property
    def query_text(self):
        return self.args.get('q', '').strip()

    @property
    def filters(self):
        _filters = []
        for q, v in self.args.items():
            if not q.startswith('filter-'):
                continue
            _, field = q.split('filter-', 1)
            _filters.append({
                "term": { field: v }
                })
        return _filters


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

        query['facets'] = {}
        for facet, size in self._facets:
            query['facets'][facet] = {'terms': {'field': facet, 'size': size}}
        
        if len(self.filters):
            _filters = self.filters if len(self.filters) == 1 else {"and": self.filters}
            base_query = query.pop('query')
            query['query'] = {
                "filtered": {
                    "query": base_query,
                    "filter": _filters
                }
            }

        self.results = es.search(index=es_index, doc_type='entity', body=query)

    def get_facet(self, name):
        if self.results is None:
            self._run()

        facet = self.results.get('facets', {}).get(name, {})
        return facet.get('terms', [])

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
