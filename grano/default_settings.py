import os

DEBUG = True
ASSETS_DEBUG = False

SECRET_KEY = 'test'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/grano.db'
APP_NAME = CELERY_APP_NAME = ES_INDEX = 'grano'
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

GITHUB_CLIENT_ID = 'da79a6b5868e690ab984'
GITHUB_CLIENT_SECRET = '1701d3bd20bbb29012592fd3a9c64b827e0682d6'

# Generate a public URI for an entity, based on its ID.
ENTITY_VIEW_PATTERN = 'http://grano.io/e/%s'
