import os
import yaml
from pprint import pprint

from grano.core import db
from grano.model import Schema
from grano.logic.schemata import save, to_dict
from grano.logic.validation import Invalid


def import_schema(project, fh):
    data = yaml.load(fh.read())
    try:
        save(project, data)
        db.session.commit()
    except Invalid, inv:
        pprint(inv.asdict())


def export_schema(project, path):
    if not os.path.exists(path):
        os.makedirs(path)
    for schema in Schema.all().filter_by(project=project):
        if schema.name == 'base':
            continue
        fn = os.path.join(path, schema.name + '.yaml')
        with open(fn, 'w') as fh:
            fh.write(yaml.dump(to_dict(schema)))
