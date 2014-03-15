from colander import Invalid
from flask import request

from grano.core import app
from grano.lib.serialisation import jsonify
from grano.views.base_api import blueprint as base_api
from grano.views.entities_api import blueprint as entities_api
from grano.views.relations_api import blueprint as relations_api
from grano.views.schemata_api import blueprint as schemata_api
from grano.views.sessions_api import blueprint as sessions_api
from grano.views.projects_api import blueprint as projects_api
from grano.views.accounts_api import blueprint as accounts_api
from grano.views.permissions_api import blueprint as permissions_api
from grano.views.auth import check_auth


@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(410)
@app.errorhandler(500)
def handle_exceptions(exc):
    message = exc.get_description(request.environ)
    message = message.replace('<p>', '').replace('</p>', '')
    body = {
        'status': exc.code,
        'name': exc.name,
        'message': message
    }
    headers = exc.get_headers(request.environ)
    return jsonify(body, status=exc.code,
        headers=headers)


@app.errorhandler(Invalid)
def handle_invalid(exc):
    body = {
        'status': 400,
        'name': 'Invalid Data',
        'message': unicode(exc),
        'errors': exc.asdict()
    }
    return jsonify(body, status=400)


app.register_blueprint(base_api)
app.register_blueprint(entities_api)
app.register_blueprint(relations_api)
app.register_blueprint(schemata_api)
app.register_blueprint(sessions_api)
app.register_blueprint(projects_api)
app.register_blueprint(accounts_api)
app.register_blueprint(permissions_api)
