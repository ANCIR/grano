from flask import Blueprint, request, session, redirect
from flask import url_for

from flask.ext.login import current_user

from grano.views.util import jsonify

sessions = Blueprint('sessions', __name__)


@sessions.route('/sessions')
def status():
    return jsonify({
        'logged_in': current_user.is_authenticated(),
        'user': current_user if current_user.is_authenticated() else None
    })
