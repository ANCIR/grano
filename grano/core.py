import logging
from flask import Flask
from flask.ext.assets import Environment
from flask.ext.sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch

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

assets = Environment(app)
db = SQLAlchemy(app)
es = Elasticsearch()

es_index = app.config.get('ES_INDEX', 'grano')
