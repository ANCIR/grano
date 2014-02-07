from flask import Blueprint, render_template
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.model import Entity
from grano.logic import entities
from grano.lib.pager import Pager
from grano.core import app


entities_api = Blueprint('entities_api', __name__)


@entities_api.route('/api/1/entities')
def index():
    query = Entity.all()
    pager = Pager(query)
    conv = lambda es: [entities.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))


@entities_api.route('/api/1/entities/<id>')
def view(id):
    return 'huhu'
