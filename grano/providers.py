import certifi

from flask import session

from grano.core import oauth, app


github = oauth.remote_app('github',
        base_url='https://github.com/login/oauth/',
        authorize_url='https://github.com/login/oauth/authorize',
        request_token_url=None,
        access_token_url='https://github.com/login/oauth/access_token',
        consumer_key=app.config.get('GITHUB_CLIENT_ID'),
        consumer_secret=app.config.get('GITHUB_CLIENT_SECRET'))


github._client.ca_certs = certifi.where()


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
