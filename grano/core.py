from flask import Flask
from flask.ext.pymongo import PyMongo
from flask.ext.assets import Environment

from grano import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('GRANO_SETTINGS', silent=True)

mongo = PyMongo(app)
assets = Environment(app)
