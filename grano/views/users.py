from flask import Blueprint, request, session, redirect
from flask import url_for

from flask.ext.login import current_user

from grano.model import User
from grano.views.pager import query_pager
from grano.views.util import jsonify, obj_or_404


blueprint = Blueprint('users', __name__)


@blueprint.route('/users')
def index():
    return query_pager(User.objects, 'users.index')


@blueprint.route('/users/<id>')
def get(id):
    user = obj_or_404(User.by_id(id))
    #require.service.view(service)
    return jsonify(user)


#@blueprint.route('/profile', methods=['GET'])
#def profile_get():
#    require.logged_in()
#    data = request.user.to_dict()
#    data['api_key'] = request.user.api_key
#    data['email'] = request.user.email
#    return jsonify(data)


#@blueprint.route('/profile', methods=['POST', 'PUT'])
#def profile_save():
#    print request.data
#    require.logged_in()
#    request.user.update(request.form)
#    db.session.commit()
#    return profile_get()
