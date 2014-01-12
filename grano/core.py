from flask import Flask
from flask.ext.assets import Environment

from mongoengine import register_connection
from grano import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('GRANO_SETTINGS', silent=True)

assets = Environment(app)

