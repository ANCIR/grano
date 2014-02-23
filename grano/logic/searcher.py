import logging 

from pprint import pprint
import elasticsearch

from grano.lib.args import arg_int
from grano.core import es, es_index


log = logging.getLogger(__name__)


class ESSearcher(object):
    """ The searcher wraps query-building for elastic search 
    queries based on request arguments. It provides a result
    interface similar to a SQLAlchemy query, so it can be 
    handled the same - especially by a pager. """

    def __init__(self, args, sort_field=None):
        self.args = args
        self.results = None
        self._limit = 25
        self._offset = 0
        self._facet_size = arg_int('facet-size', 50)
        self._facets = [(k, self._facet_size) for k in args.getlist('facet')]
        self._filters = []
        self._sort_field = sort_field

    def limit(self, limit):
        self.results = None
        self._limit = limit
        return self

    def offset(self, offset):
        self.results = None
        self._offset = offset
        return self

    def add_facet(self, name, size=None):
        if size is None:
            size = self._facet_size
        self._facets.append((name, size))

    def add_filter(self, field, value):
        self._filters.append({
            "term": { field: value }
        })

    @property
    def query_text(self):
        return self.args.get('q', '').strip()

    @property
    def filters(self):
        _filters = list(self._filters)
        for q in self.args.keys():
            if not q.startswith('filter-'):
                continue
            for v in self.args.getlist(q):
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

        #query["fields"] = ['name']
        #query["partial_fields"] = {
        #    "partial1" : {
        #        "include" : "*",
        #        "exclude" : ["inbound.*", "outbound.*", "relations.*"]
        #    }
        #}


        if self._sort_field:
            field, order = self.get_sort()
            query['sort'] = [{field: {'order': order}}]

        self.results = es.search(index=es_index, doc_type='entity',
            body=query)

    def get_sort(self):
        sort = self._sort_field
        if sort is not None:
            sort, direction = sort
        sort = self.args.get('sort', sort)
        direction = self.args.get('direction', 'asc')
        return sort, direction


    def get_facet(self, name):
        if self.results is None:
            self._run()

        facet = self.results.get('facets', {}).get(name, {})
        return facet.get('terms', [])

    def facets(self):
        if self.results is None:
            self._run()

        data = {}
        for facet, size in self._facets:
            data[facet] = self.get_facet(facet)

        return data

    def __iter__(self):
        if self.results is None:
            self._run()

        for hit in self.results.get('hits').get('hits'):
            data = hit.get('_source')
            #data = hit.get('fields')
            data['id'] = hit.get('_id')
            yield data

    def __len__(self):
        if self.results is None:
            self._run()

        return self.results.get('hits').get('total')        

    def count(self):
        return len(self)

    def all(self):
        return list(self)


def search_entities(args, sort_field=None):
    return ESSearcher(args, sort_field=sort_field)
