import uuid
import json

from slugify import slugify
from sqlalchemy.types import TypeDecorator, Unicode


def slugify_column(text):
    return slugify(text).replace('-', '_')


def make_token():
    return uuid.uuid4().get_hex()[15:]


class JSONEncodedDict(TypeDecorator):
    impl = Unicode


    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value


    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
