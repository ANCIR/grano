from flask import request, session

from grano.core import app
from grano.model import Account
from grano.lib.exc import Unauthorized


@app.before_request
def check_auth():
    api_key = request.headers.get('Authorization') \
              or request.args.get('api_key')
    if session.get('id'):
        request.account = Account.by_id(session.get('id'))
        if request.account is None:
            del session['id']
            raise Unauthorized()
    elif api_key is not None:
        request.account = Account.by_api_key(api_key)
        if request.account is None:
            raise Unauthorized()
    else: 
        request.account = None
