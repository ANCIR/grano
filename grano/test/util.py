from grano.manage import app
from grano.core import mongo_connect 


USER_FIXTURE = {
    'email': 'test_user@test.com', 
    'issuer': 'persona.test.com'
}


def make_app():
    app.config['MONGODB_DATABASE'] = 'grano_test'
    mongo_connect()
    app.config['TESTING'] = True
    _app = app.test_client()
    return _app


def make_user():
    from grano.model import User
    user = User.from_browserid(USER_FIXTURE)
    return user


def login_user(app, user):
    with app.session_transaction() as sess:
        sess['user_id'] = user.email
        sess['_fresh'] = True


def teardown_app(app):
    from mongoengine import connection
    conn = connection.get_db('default')
    for col in conn.collection_names():
        if not '.' in col:
            conn.drop_collection(col)