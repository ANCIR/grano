from flask import url_for, request
from urllib import urlencode

from grano.views.util import get_limit, get_offset, jsonify

SKIP_ARGS = ['limit', 'offset', '_']


def args(limit, offset):
    _args = [('limit', limit), ('offset', offset)]
    for k, v in request.args.items():
        if k not in SKIP_ARGS:
            _args.append((k, v))
    return '?' + urlencode(_args)


def next_url(url, count, offset, limit):
    if count < (offset + limit):
        return
    return url + args(limit, min(limit + offset, count))


def prev_url(url, count, offset, limit):
    if (offset - limit) < 0:
        return
    return url + args(limit, max(offset - limit, 0))


def query_pager(q, route, paginate=True, count=None, transform=lambda x: x, data=None, **kw):
    data = data or {}
    count = count or q.count()
    limit = get_limit()
    offset = get_offset()
    if paginate:
        results = q.skip(offset).limit(limit).all()
    else:
        results = q
    url = url_for(route, _external=True, **kw)
    data.update({
        'count': count,
        'limit': limit,
        'offset': offset,
        'previous': prev_url(url, count, offset, limit),
        'next': next_url(url, count, offset, limit),
        'results': map(transform, results)
    })
    return jsonify(data, refs=True)
