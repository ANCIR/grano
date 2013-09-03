from flask import Blueprint, request, session, redirect
from flask import url_for

from grano.core import db
from grano.model import User
from grano.auth import logged_in
from grano.auth.providers import twitter, facebook
from grano.views.util import jsonify

sessions = Blueprint('sessions', __name__)


@sessions.route('/sessions')
def status():
    return jsonify({
        'logged_in': logged_in(),
        'logout_uri': url_for('.logout', _external=True),
        'twitter_uri': url_for('.twitter_login', _external=True),
        'facebook_uri': url_for('.facebook_login', _external=True),
        'user': request.user
    })


@sessions.route('/sessions/logout')
def logout():
    #authz.require(authz.logged_in())
    session.clear()
    #flash("You've been logged out.", "success")
    return redirect(url_for('index'))


@sessions.route('/sessions/twitter/login')
def twitter_login():
    next = request.args.get('next') or None
    callback = url_for('sessions.twitter_authorized',
                       next=next, _external=True)
    return twitter.authorize(callback=callback)


@sessions.route('/sessions/twitter/callback')
@twitter.authorized_handler
def twitter_authorized(resp):
    next_url = request.args.get('next') or url_for('index')

    if resp is None:
        #flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    res = twitter.get('users/show.json',
                      data={'user_id': resp['user_id']}).data
    user = User.by_twitter_id(res['id_str'])
    if user is None:
        user_data = {
            'twitter_id': res['id_str'],
            'screen_name': res['screen_name'],
            'name': res['name']
        }
        user = User.create(user_data)
        db.session.commit()
    session['user_id'] = user.id
    return redirect(next_url)


@sessions.route('/sessions/facebook/login')
def facebook_login():
    next = request.args.get('next') or None
    callback = url_for('sessions.facebook_authorized',
                       next=next, _external=True)
    return facebook.authorize(callback=callback)


@sessions.route('/sessions/facebook/callback')
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')

    if resp is None:
        #flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['facebook_token'] = (resp['access_token'], '')
    res = facebook.get('/me').data
    user = User.by_facebook_id(res['id'])
    if user is None:
        user_data = {
            'facebook_id': res['id'],
            'screen_name': res['username'],
            'email': res['email'],
            'name': res['name']
        }
        user = User.create(user_data)
        db.session.commit()
    session['user_id'] = user.id
    return redirect(next_url)
