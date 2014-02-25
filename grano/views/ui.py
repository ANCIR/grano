import os

from flask import Blueprint, render_template, request
from flask import redirect, make_response, url_for

from grano import __version__
from grano.lib.serialisation import jsonify
from grano.core import app, url_for, app_name
from grano.views.cache import validate_cache, disable_cache
from grano.background import ping


UI_PREFIX = app.config.get('UI_PREFIX', '/')
blueprint = Blueprint('ui', __name__)

def angular_templates():
    if app.config.get('ASSETS_DEBUG'):
        return
    partials_dir = os.path.join(app.static_folder, 'templates')
    for (root, dirs, files) in os.walk(partials_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'rb') as fh:
                file_name = file_path[len(partials_dir)+1:]
                yield ('/static/templates/%s' % file_name,
                       fh.read().decode('utf-8'))


@blueprint.route(UI_PREFIX)
def index(**kw):
    return render_template('app.html', ui_root=UI_PREFIX,
        angular_templates=angular_templates())
