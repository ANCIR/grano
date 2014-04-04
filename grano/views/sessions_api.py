import requests
from flask import session, Blueprint, redirect
from flask import request


from grano import authz
from grano.lib.exc import BadRequest
from grano.lib.serialisation import jsonify
from grano.views.cache import validate_cache
from grano.core import db, url_for, app
from grano.providers import github, twitter, facebook
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

    return jsonify({
        'logged_in': authz.logged_in(),
        'api_key': request.account.api_key if authz.logged_in() else None,
        'account': request.account if request.account else None,
        'permissions': permissions
    })


def provider_not_enabled(name):
    return jsonify({
        'status': 501, 
        'name': 'Provider not configured: %s' % name,
        'message': 'There are no OAuth credentials given for %s' % name,
        }, status=501)


@blueprint.route('/api/1/sessions/logout', methods=['GET'])
def logout():
    #authz.require(authz.logged_in())
    session.clear()
    return redirect(request.args.get('next_url', '/'))


@blueprint.route('/api/1/sessions/login/github', methods=['GET'])
def github_login():
    if not app.config.get('GITHUB_CLIENT_ID'):
        return provider_not_enabled('github')
    callback=url_for('sessions_api.github_authorized')
    session.clear()
    if not request.args.get('next_url'):
        raise BadRequest("No 'next_url' is specified.")
    session['next_url'] = request.args.get('next_url')
    return github.authorize(callback=callback)


@blueprint.route('/api/1/sessions/callback/github', methods=['GET'])
@github.authorized_handler
def github_authorized(resp):
    next_url = session.get('next_url', '/')
    if resp is None or not 'access_token' in resp:
        return redirect(next_url)
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    res = requests.get('https://api.github.com/user?access_token=%s' % access_token,
            verify=False)
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


@blueprint.route('/api/1/sessions/login/twitter', methods=['GET'])
def twitter_login():
    if not app.config.get('TWITTER_API_KEY'):
        return provider_not_enabled('twitter')
    callback=url_for('sessions_api.twitter_authorized')
    session.clear()
    if not request.args.get('next_url'):
        raise BadRequest("No 'next_url' is specified.")
    session['next_url'] = request.args.get('next_url')
    return twitter.authorize(callback=callback)


@blueprint.route('/api/1/sessions/callback/twitter', methods=['GET'])
@twitter.authorized_handler
def twitter_authorized(resp):
    next_url = session.get('next_url', '/')
    if resp is None or not 'oauth_token' in resp:
        return redirect(next_url)
    
    session['twitter_token'] = (resp['oauth_token'],
        resp['oauth_token_secret'])
    res = twitter.get('users/show.json?user_id=%s' % resp.get('user_id'))
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


@blueprint.route('/api/1/sessions/login/facebook', methods=['GET'])
def facebook_login():
    if not app.config.get('FACEBOOK_APP_ID'):
        return provider_not_enabled('facebook')
    callback=url_for('sessions_api.facebook_authorized')
    session.clear()
    if not request.args.get('next_url'):
        raise BadRequest("No 'next_url' is specified.")
    session['next_url'] = request.args.get('next_url')
    return facebook.authorize(callback=callback)


@blueprint.route('/api/1/sessions/callback/facebook', methods=['GET'])
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = session.get('next_url', '/')
    if resp is None or not 'access_token' in resp:
        return redirect(next_url)
    session['facebook_token'] = (resp.get('access_token'), '')
    data = facebook.get('/me').data
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
