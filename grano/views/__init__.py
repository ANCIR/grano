#import os
from flask import request, session, render_template
#from formencode import Invalid

from grano.core import app
#from datawire.exc import Unauthorized
#from datawire.model import User


@app.before_request
def authentication():
    """ Attempt HTTP authentication via API keys on a per-request basis. """
    auth_header = request.headers.get('Authorization')
    api_key = request.args.get('api_key')
    if auth_header is not None:
        auth_type, api_key = auth_header.split(' ', 1)
    if api_key is not None:
        try:
            request.user = User.by_api_key(api_key)
        except:
            raise Unauthorized('Invalid API key.')
    elif 'user_id' in session:
        request.user = User.by_id(session['user_id'])
    else:
        request.user = None



@app.route("/")
def index(path=None):
    return render_template('layout.html')
