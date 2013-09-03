import os

DEBUG = True
ASSETS_DEBUG = True

SECRET_KEY = os.environ.get('GRANO_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'

