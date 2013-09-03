from flask import Response, request, url_for

from datawire.exc import NotFound
from datawire.util import JSONEncoder

BOOL_TRUISH = ['true', '1', 'yes', 'y', 't']


def obj_or_404(obj):
    if obj is None:
        NotFound()
    return obj


def arg_bool(name, default=False):
    v = request.args.get(name, '')
    if not len(v):
        return default
    return v in BOOL_TRUISH


def arg_int(name, default=None):
    try:
        v = request.args.get(name)
        return int(v)
    except (ValueError, TypeError):
        return default


def get_limit(default=50):
    return max(0, min(1000, arg_int('limit', default=default)))


def get_offset(default=0):
    return max(0, arg_int('offset', default=default))


def jsonify(obj, status=200, headers=None, refs=False):
    """ Custom JSONificaton to support obj.to_dict protocol. """
    data = JSONEncoder(refs=refs).encode(obj)
    if 'callback' in request.args:
        cb = request.args.get('callback')
        data = '%s && %s(%s)' % (cb, cb, data)
    return Response(data, headers=headers,
                    status=status, mimetype='application/json')
