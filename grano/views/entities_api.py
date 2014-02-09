from flask import Blueprint, render_template
from flask import redirect, make_response, url_for

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404
from grano.model import Entity
from grano.logic import entities, relations
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
    entity = object_or_404(Entity.by_id(id))
    return jsonify(entities.to_rest(entity))


@entities_api.route('/api/1/entities/<id>/inbound')
def inbound(id):
    entity = object_or_404(Entity.by_id(id))
    pager = Pager(entity.inbound)
    conv = lambda es: [relations.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))


@entities_api.route('/api/1/entities/<id>/outbound')
def outbound(id):
    entity = object_or_404(Entity.by_id(id))
    pager = Pager(entity.outbound)
    conv = lambda es: [relations.to_rest_index(e) for e in es]
    return jsonify(pager.to_dict(conv))
