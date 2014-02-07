import math
from urllib import urlencode
from flask import url_for, request

from grano.lib.args import arg_int, get_limit


class Pager(object):

    def __init__(self, query, name, limit=25, pager_range=4, **kwargs):
        self.args = request.args
        self.name = name
        self.query = query
        self.kwargs = kwargs
        self.pager_range = pager_range
        self.page = arg_int(name + '_page', default=1)
        self.limit = get_limit(default=limit, field=name + '_limit')
        
    @property
    def offset(self):
        return (self.page-1)*self.limit

    @property
    def pages(self):
        return int(math.ceil(len(self)/float(self.limit)))

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def next_url(self):
        return self.page_url(self.page + 1) if self.has_next \
               else self.page_url(self.page)

    @property
    def prev_url(self):
        return self.page_url(self.page - 1) if self.has_prev \
               else self.page_url(self.page)

    @property
    def query_args(self):
        args = []
        for key in self.args:
            if key == self.name + '_page':
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
        query_args = [t for t in self.query_args if \
                t != (arg, value.encode('utf-8'))]
        return self.url(query_args)

    def page_url(self, page):
        return self.add_url_state(self.name + '_page', page)

    def url(self, query):
        url = url_for(request.endpoint, **dict(self.kwargs))
        if len(query):
            qs = urlencode(query)
            url = url + '?' + qs
        return url + '#' + self.name

    def __iter__(self):
        query = self.query
        query = query.limit(self.limit)
        query = query.offset(self.offset)
        return query.all().__iter__()

    def __len__(self):
        return self.query.count()


