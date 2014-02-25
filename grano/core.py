import logging

from flask import Flask, url_for as _url_for
from flask.ext.assets import Environment
from flask.ext.oauth import OAuth
from flask.ext.sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
from celery import Celery

from grano import default_settings

logging.basicConfig(level=logging.DEBUG)

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

urllib3_log = logging.getLogger("urllib3")
urllib3_log.setLevel(logging.WARNING)

elasticsearch_log = logging.getLogger("elasticsearch")
elasticsearch_log.setLevel(logging.WARNING)

#sqlalchemy_log = logging.getLogger("sqlalchemy")
#sqlalchemy_log.setLevel(logging.INFO)


app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('GRANO_SETTINGS', silent=True)
app_name = app.config.get('APP_NAME', 'grano')

assets = Environment(app)
db = SQLAlchemy(app)
es = Elasticsearch()
celery = Celery(app.config.get('CELERY_APP_NAME', app_name),
    broker=app.config['CELERY_BROKER_URL'])
celery.config_from_object(app.config)

es_index = app.config.get('ES_INDEX', app_name)


oauth = OAuth()

def url_for(*a, **kw):
    return _url_for(*a, _external=True, **kw)
