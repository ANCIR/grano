from hashlib import sha1

from werkzeug.http import is_resource_modified
from flask import Response, request

from grano.core import app


class NotModified(Exception):
    pass


@app.errorhandler(NotModified)
def handle_not_modified(exc):
    return Response(status=304)


def generate_etag(keys):
    args = sorted(set(request.args.items() + keys.items()))
    args = filter(lambda (k,v): k != '_', args) # jquery where is your god now?!?
    args = [k + ':' + repr(v) for k, v in args]
    return sha1('|'.join(args)).hexdigest()


def validate_cache(keys=None, last_modified=None):
    if isinstance(last_modified, (list, tuple)):
        last_modified = max(last_modified)
    if keys is None or not isinstance(keys, dict):
        keys = {'keys': keys}
    keys['last_modified'] = last_modified
    request._grano_etag = generate_etag(keys)
    request._grano_modified = last_modified
    if not is_resource_modified(request.environ,
        etag=request._grano_etag,
        last_modified=last_modified):
        raise NotModified()
    if request.if_none_match == request._grano_etag:
        raise NotModified()


def disable_cache():
    request.no_cache = True


@app.before_request
def setup_cache():
    request._grano_etag = None
    request._grano_modified = None
    request.no_cache = False


@app.after_request
def configure_cache_headers(response_class):
    if (not app.config.get('CACHE')) or request.no_cache:
        return response_class
    if request.method in ['GET', 'HEAD', 'OPTIONS'] \
        and response_class.status_code < 400 \
        and not response_class.is_streamed:
        response_class.cache_control.max_age = app.config.get('CACHE_AGE')
        
        if request.account is not None:
            response_class.cache_control.must_revalidate = True
            response_class.cache_control.private = True
        else:
            response_class.cache_control.public = True
        if request._grano_modified:
            response_class.last_modified = request._grano_modified
        if request._grano_etag:
            response_class.add_etag(request._grano_etag)    
    return response_class
