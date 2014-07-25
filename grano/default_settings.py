from kombu import Exchange, Queue

DEBUG = True
ASSETS_DEBUG = False

# For production, it's essential that this is set:

SECRET_KEY = 'test'
CACHE = True
CACHE_AGE = 84600

# Configure the database

SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/grano'
APP_NAME = CELERY_APP_NAME = ES_INDEX = 'grano'




# You need to create an application on GitHub which can be used
# for OAuth sign-in.

#GITHUB_CLIENT_ID = 'da79a6b5868e690ab984'
#GITHUB_CLIENT_SECRET = '1701d3bd20bbb29012592fd3a9c64b827e0682d6'

#TWITTER_API_KEY = 'UZYoBAfBzNluBlmBwPOGYw'
#TWITTER_API_SECRET = 'ngHaeaRPKA5BDQNXhPFmLWA1PvTA1kBGDaAJmc517E'

#FACEBOOK_APP_ID = '647877358607044'
#FACEBOOK_APP_SECRET = '5cb5c2181d0dc6976e97a55f90330165'


# Generate a public URI for an entity, based on its ID.

ENTITY_VIEW_PATTERN = 'http://beta.grano.cc/entities/%s'


# Asynchronous task processing: For some tasks, grano will run
# some processing work in a delayed process, connected via a
# queue. If you do not wish to use delayed processing, you can
# turn it off with:

CELERY_ALWAYS_EAGER = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_DEFAULT_QUEUE = CELERY_APP_NAME + '_q'
CELERY_QUEUES = (
    Queue(CELERY_DEFAULT_QUEUE, Exchange(CELERY_DEFAULT_QUEUE),
          routing_key=CELERY_DEFAULT_QUEUE),
)

# Otherwise, just set the task broker URI which you intend to
# use:

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

PLUGINS = []
