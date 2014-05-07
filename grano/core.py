import os

from flask import Flask, url_for as _url_for
from flask.ext.oauth import OAuth
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate
from celery import Celery

from grano import default_settings
from grano import constants, logs


app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_object(constants)
app.config.from_envvar('GRANO_SETTINGS', silent=True)
app_name = app.config.get('APP_NAME', 'grano')

db = SQLAlchemy(app)

ALEMBIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                              '../alembic'))
migrate = Migrate(app, db, directory=ALEMBIC_DIR)

celery = Celery(app.config.get('CELERY_APP_NAME', app_name),
                broker=app.config['CELERY_BROKER_URL'])
celery.config_from_object(app.config)

oauth = OAuth()


def url_for(*a, **kw):
    try:
        return _url_for(*a, _external=True, **kw)
    except RuntimeError:
        return None
