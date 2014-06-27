from functools import wraps
import certifi

from flask import session

from grano.core import oauth, app
from grano.lib.serialisation import jsonify


class Stub():
    """ A stub authorization handler to sit in for auth methods that
    are not currently enabled. """

    def __init__(self, name):
        self.name = name

    def authorize(self, **kwargs):
        return jsonify({
            'status': 501,
            'name': 'Provider not configured: %s' % self.name,
            'message': 'There are no credentials given for %s' % self.name,
            }, status=501)

    def authorized_handler(self, f):
        @wraps(f)
        def inner(*a, **kw):
            return self.authorize()
        return inner


PROVIDERS = {
    'github': Stub('github'),
    'twitter': Stub('twitter'),
    'facebook': Stub('facebook')
}


if app.config.get('GITHUB_CLIENT_ID') is not None:
    PROVIDERS['github'] = oauth.remote_app('github',
        base_url='https://github.com/login/oauth/',
        authorize_url='https://github.com/login/oauth/authorize',
        request_token_url=None,
        access_token_url='https://github.com/login/oauth/access_token',
        consumer_key=app.config.get('GITHUB_CLIENT_ID'),
        consumer_secret=app.config.get('GITHUB_CLIENT_SECRET'))
    PROVIDERS['github']._client.ca_certs = certifi.where()

if app.config.get('TWITTER_API_KEY') is not None:
    twitter = oauth.remote_app('twitter',
        base_url='https://api.twitter.com/1.1/',
        request_token_url='https://api.twitter.com/oauth/request_token',
        access_token_url='https://api.twitter.com/oauth/access_token',
        authorize_url='https://api.twitter.com/oauth/authenticate',
        consumer_key=app.config.get('TWITTER_API_KEY'),
        consumer_secret=app.config.get('TWITTER_API_SECRET'))

    @twitter.tokengetter
    def get_twitter_token(token=None):
        return session.get('twitter_token')

    PROVIDERS['twitter'] = twitter

if app.config.get('FACEBOOK_APP_ID') is not None:
    facebook = oauth.remote_app('facebook',
        base_url='https://graph.facebook.com/',
        request_token_url=None,
        access_token_url='/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        consumer_key=app.config.get('FACEBOOK_APP_ID'),
        consumer_secret=app.config.get('FACEBOOK_APP_SECRET'),
        request_token_params={'scope': 'email'})

    @facebook.tokengetter
    def get_facebook_token(token=None):
        return session.get('facebook_token')

    PROVIDERS['facebook'] = facebook

