import yaml

from grano.core import db
from grano.model import Schema


def import_schema(path):
	with open(path, 'r') as fh:
		data = yaml.load(fh.read())
		for schema in data:
			Schema.from_dict(schema)
		db.session.commit()

def export_schema(path):
	with open(path, 'w') as fh:
		data = [s.to_dict() for s in Schema.all()]
		fh.write(yaml.dump(data))
