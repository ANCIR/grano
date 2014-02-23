import os

DEBUG = True
ASSETS_DEBUG = False

# For production, it's essential that this is set:

SECRET_KEY = 'test'
CACHE = True
CACHE_AGE = 84600

# Configure the database

SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/grano.db'
APP_NAME = CELERY_APP_NAME = ES_INDEX = 'grano'


# You need to create an application on GitHub which can be used 
# for OAuth sign-in. 

GITHUB_CLIENT_ID = 'da79a6b5868e690ab984'
GITHUB_CLIENT_SECRET = '1701d3bd20bbb29012592fd3a9c64b827e0682d6'


# Generate a public URI for an entity, based on its ID.

ENTITY_VIEW_PATTERN = 'http://beta.grano.cc/entities/%s'


# Asynchronous task processing: For some tasks, grano will run 
# some processing work in a delayed process, connected via a 
# queue. If you do not wish to use delayed processing, you can 
# turn it off with: 

CELERY_ALWAYS_EAGER = True

# Otherwise, just set the task broker URI which you intend to 
# use:

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
