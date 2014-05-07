from grano.core import db
from grano.manage import app
from grano.test.fixtures import create_fixtures


def make_test_app(use_cookies=False):
    app.config['TESTING'] = True
    app.config['CACHE'] = False
    app.config['PLUGINS'] = []
    app.config['CELERY_ALWAYS_EAGER'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.create_all()
    create_fixtures()

    return app.test_client(use_cookies=use_cookies)


def tear_down_test_app():
    #db.session.rollback()
    db.drop_all()

