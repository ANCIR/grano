import os
import yaml

from grano.core import db
from grano.model import Schema


def import_schema(fh):
    data = yaml.load(fh.read())
    Schema.from_dict(data)
    db.session.commit()


def export_schema(path):
    if not os.path.exists(path):
        os.makedirs(path)
    for schema in Schema.all():
        if schema.name == 'base':
            continue
        fn = os.path.join(path, schema.name + '.yaml')
        with open(fn, 'w') as fh:
            fh.write(yaml.dump(schema.to_dict()))
