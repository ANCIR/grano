from colander import Invalid
from flask import request

from grano.core import app
from grano.lib.serialisation import jsonify
from grano.views.base_api import base_api
from grano.views.entities_api import entities_api


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
        'description': unicode(exc),
        'errors': exc.asdict()
    }
    return jsonify(body, status=400)


app.register_blueprint(base_api)
app.register_blueprint(entities_api)
