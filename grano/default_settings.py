import os

DEBUG = True
ASSETS_DEBUG = False

SECRET_KEY = 'test'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/grano.db'
ES_INDEX = 'grano'

# Generate a public URI for an entity, based on its ID.
ENTITY_VIEW_PATTERN = 'http://grano.io/e/%s'
