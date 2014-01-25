import math

from flask import url_for, request

class Pager(object):

    def __init__(self, query, name, limit=25, pager_range=3, **kwargs):
        self.args = request.args
        self.name = name
        self.query = query
        self.kwargs = kwargs
        self.pager_range = pager_range

        try:
            self.page = int(request.args.get(name + '_page'))
        except:
            self.page = 1
        try:
            self.limit = min(int(request.args.get(name + '_limit')), 200)
        except:
            self.limit = limit

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
        return [(k, v.encode('utf-8')) for k, v in self.args.items() \
                if k != self.name + '_page']

    @property
    def range(self):
        low = self.page - self.pager_range
        high = self.page + self.pager_range

        if low < 1:
            low = 1
            high = min([(2*self.pager_range)+1, len(self)])
        
        if high > len(self):
            high = len(self)
            low = max([1, len(self) - (2*self.pager_range)+1])

        return range(low, high+1)


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
        kw = dict(query)
        kw.update(self.kwargs)
        return url_for(request.endpoint, **dict(kw)) + '#' + self.name

    def __iter__(self):
        query = self.query
        query = query.limit(self.limit)
        query = query.offset(self.offset)
        return query.all().__iter__()

    def __len__(self):
        return self.query.count()


