from datetime import timedelta
import os

DEBUG = os.getenv("GRANO_DEBUG", True)
ASSETS_DEBUG = False
DEBUG_TIMING = False

# For production, it's essential that this is set:

SECRET_KEY = os.getenv("GRANO_SECRET_KEY", "test")
CACHE = True
CACHE_AGE = 84600

# Configure the database

SQLALCHEMY_DATABASE_URI = os.getenv("GRANO_DATABASE", "postgresql://grano:grano@postgres/grano")
APP_NAME = CELERY_APP_NAME = ES_INDEX = os.getenv("GRANO_APP_NAME", "grano")

# Force HTTPS here:
PREFERRED_URL_SCHEME = os.getenv("GRANO_URL_SCHEME", "http")

# You need to create an application on GitHub which can be used
# for OAuth sign-in.

GITHUB_CLIENT_ID = os.getenv("GRANO_GITHUB_CLIENT_ID", "da79a6b5868e690ab984")
GITHUB_CLIENT_SECRET = os.getenv("GRANO_GITHUB_CLIENT_SECRET", "1701d3bd20bbb29012592fd3a9c64b827e0682d6")

# TWITTER_API_KEY = 'UZYoBAfBzNluBlmBwPOGYw'
# TWITTER_API_SECRET = 'ngHaeaRPKA5BDQNXhPFmLWA1PvTA1kBGDaAJmc517E'

# FACEBOOK_APP_ID = '647877358607044'
# FACEBOOK_APP_SECRET = '5cb5c2181d0dc6976e97a55f90330165'

# Asynchronous task processing: For some tasks, grano will run
# some processing work in a delayed process, connected via a
# queue. If you do not wish to use delayed processing, you can
# turn it off with:

CELERY_ALWAYS_EAGER = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

CELERYBEAT_SCHEDULE = {
    'periodic-tasks': {
        'task': 'grano.background.periodic',
        'schedule': timedelta(minutes=30)
    },
}

CELERY_TIMEZONE = 'UTC'

# Otherwise, just set the task broker URI which you intend to
# use:

CELERY_BROKER_URL = os.getenv("GRANO_CELERY_BROKER", "amqp://guest:guest@rabbitmq:5672")

DEFAULT_PLUGINS = ['degrees', 'bidi_create', 'bidi_refresh', 'levenshtein']
PLUGINS = ['ui']
