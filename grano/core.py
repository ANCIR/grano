from flask import Flask
from flask.ext.assets import Environment

from mongoengine import register_connection
from grano import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('GRANO_SETTINGS', silent=True)

assets = Environment(app)

register_connection('default',
    app.config.get('MONGODB_DATABASE', 'grano'),
    host=app.config.get('MONGODB_HOST', 'localhost'),
    port=app.config.get('MONGODB_PORT', 27017),
    username=app.config.get('MONGODB_USERNAME'),
    password=app.config.get('MONGODB_PASSWORD'))
