from flask import Blueprint, render_template
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404
from grano.model import Schema
from grano.logic import schemata
from grano.lib.pager import Pager
from grano.core import app


schemata_api = Blueprint('schemata_api', __name__)


@schemata_api.route('/api/1/schemata')
def index():
    query = Schema.all()
    pager = Pager(query)
    conv = lambda es: [schemata.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))


@schemata_api.route('/api/1/schemata/<name>')
def view(name):
    schema = object_or_404(Schema.by_name(name))
    return jsonify(schemata.to_rest(schema))
