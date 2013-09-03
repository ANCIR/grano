from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

from grano.core import db, assets
from grano.views import app

manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))

@manager.command
def createdb():
    """ Create the database entities. """
    db.create_all()

if __name__ == "__main__":
    manager.run()
