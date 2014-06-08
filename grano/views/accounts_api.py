from flask import Blueprint, render_template, request, Response
from flask import redirect, make_response
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased

from grano.lib.serialisation import jsonify
from grano.lib.args import object_or_404, request_data
from grano.model import Account
from grano.logic import accounts
from grano.core import db
from grano.lib.pager import Pager
from grano.views.cache import validate_cache
from grano import authz


blueprint = Blueprint('accounts_api', __name__)


@blueprint.route('/api/1/accounts/_suggest', methods=['GET'])
def suggest():
    authz.require(authz.logged_in())
    query = request.args.get('q', '') + '%'
    q = db.session.query(Account)
    q = q.filter(or_(Account.full_name.ilike(query),
                     Account.login.ilike(query),
                     Account.email.ilike(query)))
    pager = Pager(q)

    def convert(accounts):
        data = []
        for account in accounts:
            data.append({
                'display_name': account.display_name,
                'id': account.id
            })
        return data

    validate_cache(keys='#'.join([d.display_name for d in pager]))
    return jsonify(pager.to_dict(results_converter=convert))


@blueprint.route('/api/1/accounts/<id>', methods=['GET'])
def view(id):
    account = object_or_404(Account.by_id(id))
    return jsonify(account)


@blueprint.route('/api/1/accounts/<id>', methods=['POST', 'PUT'])
def update(id):
    account = object_or_404(Account.by_id(id))
    authz.require(account.id == request.account.id)
    data = request_data()
    account = accounts.save(data, account=account)
    db.session.commit()
    return jsonify(account)
