import math
from urllib import urlencode
from flask import request

from grano.core import url_for
from grano.lib.args import arg_int, get_limit


class Pager(object):

    def __init__(self, query, name=None, limit=25, pager_range=4, **kwargs):
        self.args = request.args
        self.name = name
        self.query = query
        self.kwargs = kwargs
        self.pager_range = pager_range
        self.offset = arg_int(self.arg_name('offset'), default=0)
        self.limit = get_limit(default=limit, field=self.arg_name('limit'))
        self._results = None

    def arg_name(self, arg):
        if self.name is None:
            return arg
        return self.name + '_' + arg

    @property
    def page(self):
        if self.limit == 0:
            return 1
        return (self.offset/self.limit) + 1

    @property
    def pages(self):
        if self.limit == 0:
            return 1
        return int(math.ceil(len(self)/float(self.limit)))

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def next_url(self):
        if not self.has_next:
            return None
        return self.page_url(self.page + 1) if self.has_next \
               else self.page_url(self.page)

    @property
    def prev_url(self):
        if not self.has_prev:
            return None
        return self.page_url(self.page - 1) if self.has_prev \
               else self.page_url(self.page)

    @property
    def query_args(self):
        args = []
        for key in self.args:
            if key == self.arg_name('offset'):
                continue
            for value in self.args.getlist(key):
                args.append((key, value.encode('utf-8')))
        return args

    @property
    def range(self):
        low = self.page - self.pager_range
        high = self.page + self.pager_range

        if low < 1:
            low = 1
            high = min((2*self.pager_range)+1, self.pages)

        if high > self.pages:
            high = self.pages
            low = max(1, self.pages - (2*self.pager_range)+1)

        return range(low, high+1)

    def has_url_state(self, arg, value):
        return (arg, unicode(value).encode('utf-8')) in self.query_args

    def add_url_state(self, arg, value):
        query_args = self.query_args
        query_args.append((arg, unicode(value).encode('utf-8')))
        return self.url(query_args)

    def remove_url_state(self, arg, value):
        query_args = [t for t in self.query_args if
                      t != (arg, value.encode('utf-8'))]
        return self.url(query_args)

    def page_url(self, page):
        return self.add_url_state(self.arg_name('offset'), (page-1)*self.limit)

    def url(self, query):
        url = url_for(request.endpoint, **dict(self.kwargs))
        if len(query):
            qs = urlencode(query)
            url = url + '?' + qs
        if self.name is not None:
            url = url + '#' + self.name
        return url

    def __iter__(self):
        if self._results is None:
            query = self.query
            query = query.limit(self.limit)
            query = query.offset(self.offset)
            self._results = query.all()
        return self._results.__iter__()

    def __len__(self):
        return self.query.count()

    def cache_keys(self):
        # TODO: consider including count.
        keys = {}
        for i, res in enumerate(self):
            k = res.id if hasattr(res, 'id') else repr(res)
            keys[str(i)] = k
        return keys

    def to_dict(self, results_converter=lambda r: r):
        format_args = [(k, v) for (k, v) in self.query_args if k != 'limit']
        format_args.extend([('limit', 'LIMIT'), ('offset', 'OFFSET')])
        return {
            'next_url': self.next_url,
            'prev_url': self.prev_url,
            'format': self.url(format_args),
            'total': len(self),
            'page': self.page,
            'pages': self.pages,
            'limit': self.limit,
            'offset': self.offset,
            'results': results_converter(list(self))
        }
