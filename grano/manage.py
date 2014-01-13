from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

from grano.core import db, assets, app
#from grano.views import app
#from grano.io import import_schema, export_schema


manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))


@manager.command
def createdb():
    """ Create the database schema. """
    db.create_all()


@manager.command
def schema_import(path):
    """ Load a schema specification from a YAML file. """
    import_schema(path)


@manager.command
def schema_export(path):
    """ Export the current schema to a YAML file. """
    export_schema(path)


if __name__ == "__main__":
    manager.run()
