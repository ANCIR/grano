from grano.manage import app
from grano.core import mongo_connect 

def make_app():
    app.config['MONGODB_DATABASE'] = 'grano_test'
    mongo_connect()
    app.config['TESTING'] = True
    _app = app.test_client()
    return _app

def teardown_app(app):
    from mongoengine import connection
    conn = connection.get_db('default')
    for col in conn.collection_names():
        if not '.' in col:
            conn.drop_collection(col)