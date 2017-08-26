import os
import pkg_resources

from flask import Flask, url_for as flask_url_for
from flask_oauth import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from kombu import Exchange, Queue
from celery import Celery

from grano import default_settings
from grano import constants, logs # noqa


app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_object(constants)
app.config.from_envvar('GRANO_SETTINGS', silent=True)

app_name = app.config.get('APP_NAME', 'grano')
app_version = pkg_resources.require('grano')[0].version

db = SQLAlchemy(app)

ALEMBIC_DIR = os.path.join(os.path.dirname(__file__), 'alembic')
ALEMBIC_DIR = os.path.abspath(ALEMBIC_DIR)
migrate = Migrate(app, db, directory=ALEMBIC_DIR)

queue_name = app.config.get('CELERY_APP_NAME') + '_q'
app.config['CELERY_DEFAULT_QUEUE'] = queue_name
app.config['CELERY_QUEUES'] = (
    Queue(queue_name, Exchange(queue_name), routing_key=queue_name),
)


celery = Celery(app.config.get('CELERY_APP_NAME', app_name),
                broker=app.config['CELERY_BROKER_URL'])
celery.config_from_object(app.config)

oauth = OAuth()


def url_for(*a, **kw):
    """Generate external URLs with HTTPS (if configured)."""
    try:
        kw['_external'] = True
        if app.config.get('PREFERRED_URL_SCHEME'):
            kw['_scheme'] = app.config.get('PREFERRED_URL_SCHEME')
        return flask_url_for(*a, **kw)
    except RuntimeError:
        return None
