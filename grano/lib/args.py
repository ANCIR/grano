import json

from flask import request
from restpager.args import arg_bool, arg_int, get_limit, get_offset # noqa
from grano.lib.exc import BadRequest, NotFound


def request_data(overlay={}):
    """ Decode a JSON-formatted POST body. """
    data = request.json
    if data is None:
        try:
            data = json.loads(request.form.get('data'))
        except (ValueError, TypeError):
            data = dict(request.form.items())
    data.update(overlay)
    return data


def object_or_404(obj):
    if obj is None:
        raise NotFound()
    return obj


def single_arg(name, default=None):
    vals = [v for v in request.args.getlist(name) if v.strip()]
    if len(vals) == 0:
        return default
    elif len(vals) > 1:
        raise BadRequest('Too many values given for: %s' % name)
    else:
        return vals[0]
