import os

DEBUG = True
ASSETS_DEBUG = False

SECRET_KEY = 'test'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/grano.db'
ES_INDEX = 'grano'

# Generate a public URI for an entity, based on its ID.
ENTITY_VIEW_PATTERN = 'http://grano.io/e/%s'

# OpenCorporates recon daemon config
#
# OPENCORPORATES_URL = 'http://opencorporates.com/reconcile'
# OPENCORPORATES_APIKEY = 'xxx'
# OPENCORPORATES_SCORE_LIMIT = 90 # cut-off for auto-recon
# OPENCORPORATES_SCHEMATA = ['company'] # select the schemata which trigger recon
# OPENCORPORATES_COUNTRY_CODE = 'country_code' # property name with an iso 2-letter country code
