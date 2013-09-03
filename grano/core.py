from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment

from grano import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('GRANO_SETTINGS', silent=True)

db = SQLAlchemy(app)
assets = Environment(app)
