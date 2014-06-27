import requests
from flask import session, Blueprint, redirect
from flask import request


from grano import authz
from grano.lib.exc import BadRequest
from grano.lib.serialisation import jsonify
from grano.views.cache import validate_cache
from grano.core import db, url_for
from grano.providers import PROVIDERS, Stub
from grano.model import Account
from grano.logic import accounts


blueprint = Blueprint('sessions_api', __name__)


@blueprint.route('/api/1/sessions', methods=['GET'])
def status():
    permissions = {}
    if authz.logged_in():
        for permission in request.account.permissions:
            permissions[permission.project.slug] = {
                'reader': permission.reader,
                'editor': permission.editor,
                'admin': permission.admin
            }

    keys = {
        'p': repr(permissions),
        'i': request.account.id if authz.logged_in() else None
    }
    validate_cache(keys=keys)

    oauth_providers = {}
    for name, provider in PROVIDERS.items():
        if not isinstance(provider, Stub):
            oauth_providers[name] = url_for('.login', provider=name)

    return jsonify({
        'logged_in': authz.logged_in(),
        'api_key': request.account.api_key if authz.logged_in() else None,
        'account': request.account if request.account else None,
        'permissions': permissions,
        'oauth_providers': oauth_providers
    })


@blueprint.route('/api/1/sessions/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(request.args.get('next_url', '/'))


@blueprint.route('/api/1/sessions/login/<provider>', methods=['GET'])
def login(provider):
    if provider not in PROVIDERS:
        raise BadRequest('Unknown provider: %s' % provider)
    callback = url_for('sessions_api.%s_authorized' % provider)
    session.clear()
    if not request.args.get('next_url'):
        raise BadRequest("No 'next_url' is specified.")
    session['next_url'] = request.args.get('next_url')
    return PROVIDERS[provider].authorize(callback=callback)


handler = PROVIDERS.get('github')


@blueprint.route('/api/1/sessions/callback/github', methods=['GET'])
@handler.authorized_handler
def github_authorized(resp):
    next_url = session.get('next_url', '/')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    url = 'https://api.github.com/user?access_token=%s'
    res = requests.get(url % access_token, verify=False)
    data = res.json()
    account = Account.by_github_id(data.get('id'))
    data_ = {
        'full_name': data.get('name'),
        'login': data.get('login'),
        'email': data.get('email'),
        'github_id': data.get('id')
    }
    account = accounts.save(data_, account=account)
    db.session.commit()
    session['id'] = account.id
    return redirect(next_url)


handler = PROVIDERS.get('twitter')


@blueprint.route('/api/1/sessions/callback/twitter', methods=['GET'])
@handler.authorized_handler
def twitter_authorized(resp):
    next_url = session.get('next_url', '/')
    if resp is None or 'oauth_token' not in resp:
        return redirect(next_url)
    session['twitter_token'] = (resp['oauth_token'],
                                resp['oauth_token_secret'])
    provider = PROVIDERS.get('twitter')
    res = provider.get('users/show.json?user_id=%s' % resp.get('user_id'))
    account = Account.by_twitter_id(res.data.get('id'))
    data_ = {
        'full_name': res.data.get('name'),
        'login': res.data.get('screen_name'),
        'twitter_id': res.data.get('id')
    }
    account = accounts.save(data_, account=account)
    db.session.commit()
    session['id'] = account.id
    return redirect(next_url)


handler = PROVIDERS.get('facebook')


@blueprint.route('/api/1/sessions/callback/facebook', methods=['GET'])
@handler.authorized_handler
def facebook_authorized(resp):
    next_url = session.get('next_url', '/')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)
    session['facebook_token'] = (resp.get('access_token'), '')
    data = PROVIDERS.get('facebook').get('/me').data
    account = Account.by_facebook_id(data.get('id'))
    data_ = {
        'full_name': data.get('name'),
        'login': data.get('username'),
        'email': data.get('email'),
        'facebook_id': data.get('id')
    }
    account = accounts.save(data_, account=account)
    db.session.commit()
    session['id'] = account.id
    return redirect(next_url)
