from flask import Blueprint, render_template
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404
from grano.model import Relation
from grano.logic import relations
from grano.lib.pager import Pager
from grano.core import app


relations_api = Blueprint('relations_api', __name__)


@relations_api.route('/api/1/relations')
def index():
    query = Relation.all()
    pager = Pager(query)
    conv = lambda es: [relations.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))


@relations_api.route('/api/1/relations/<id>')
def view(id):
    relation = object_or_404(Relation.by_id(id))
    return jsonify(relations.to_rest(relation))
