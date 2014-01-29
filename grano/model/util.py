import uuid
from slugify import slugify


def slugify_column(text):
    return slugify(text).replace('-', '_')


def make_token():
    return uuid.uuid4().get_hex()[15:]
