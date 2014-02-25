from flask import Blueprint, render_template, request, Response
from flask import redirect, make_response
from sqlalchemy.orm import aliased

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Account
from grano.logic import accounts
from grano.core import app, db, url_for
from grano import authz


blueprint = Blueprint('accounts_api', __name__)


@blueprint.route('/api/1/accounts/<id>', methods=['GET'])
def view(id):
    account = object_or_404(Account.by_id(id))
    return jsonify(accounts.to_rest(account))


@blueprint.route('/api/1/accounts/<id>', methods=['POST', 'PUT'])
def update(id):
    account = object_or_404(Account.by_id(id))
    authz.require(account.id==request.account.id)
    data = request_data()
    entity = accounts.save(data, account=account)
    db.session.commit()
    return jsonify(accounts.to_rest(account))
