from flask import session
from flask.ext.oauth import OAuth

from grano.core import app

oauth = OAuth()

twitter = oauth.remote_app('twitter',
        base_url='https://api.twitter.com/1.1/',
        authorize_url='https://api.twitter.com/oauth/authorize',
        request_token_url='https://api.twitter.com/oauth/request_token',
        access_token_url='https://api.twitter.com/oauth/access_token',
        consumer_key=app.config.get('TWITTER_CONSUMER_KEY'),
        consumer_secret=app.config.get('TWITTER_CONSUMER_SECRET'))

facebook = oauth.remote_app('facebook',
        base_url='https://graph.facebook.com/',
        request_token_url=None,
        access_token_url='/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        consumer_key=app.config.get('FACEBOOK_APP_ID'),
        consumer_secret=app.config.get('FACEBOOK_APP_SECRET'),
        request_token_params={'scope': 'email'})


@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')


@facebook.tokengetter
def get_facebook_token(token=None):
    return session.get('facebook_token')
