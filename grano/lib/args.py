from flask import request
from grano.lib.exc import BadRequest, NotFound


BOOL_TRUISH = ['true', '1', 'yes', 'y', 't']


def arg_bool(name, default=False):
    """ Fetch a query argument, as a boolean. """
    v = request.args.get(name, '')
    if not len(v):
        return default
    return v in BOOL_TRUISH


def arg_int(name, default=None):
    """ Fetch a query argument, as an integer. """
    try:
        v = request.args.get(name)
        return int(v)
    except (ValueError, TypeError):
        return default


def get_limit(default=50, field='limit'):
    """ Get a limit argument. """
    return max(0, min(1000, arg_int(field, default=default)))


def get_offset(default=0, field='offset'):
    """ Get an offset argument. """
    return max(0, arg_int(field, default=default))


def request_data(overlay={}):
    """ Decode a JSON-formatted POST body. """
    data = request.json
    if data is None:
        data = dict(request.form.items())
    data.update(overlay)
    return data


def object_or_404(obj):
    if obj is None:
        raise NotFound()
    return obj


def single_arg(args, name, default=None):
    vals = [v for v in args.getlist(name) if v.strip()]
    if len(vals) == 0:
        return default
    elif len(vals) > 1:
        raise BadRequest('Too many values given for: %s' % name)
    else:
        return vals[0]
