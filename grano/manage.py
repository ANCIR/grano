import logging 

from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

from grano.core import db, assets
from grano.views import app
from grano.service import import_schema, export_schema
from grano.service import import_aliases, export_aliases
from grano.service import index_entities, index_single
from grano.service import flush_entities
from grano.logic.searcher import search_entities
from grano.service import generate_sitemap


log = logging.getLogger('grano')
manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))


@manager.command
def createdb():
    """ Create the database schema. """
    db.create_all()
    with app.open_resource('fixtures/base.yaml') as fh:
        import_schema(fh)


@manager.command
def schema_import(path):
    """ Load a schema specification from a YAML file. """
    with open(path, 'r') as fh:
        import_schema(fh)


@manager.command
def schema_export(path):
    """ Export the current schema to a YAML file. """
    export_schema(path)


@manager.command
def alias_import(path):
    """ Load a set of entity aliases from a CSV file. """
    import_aliases(path)


@manager.command
def alias_export(path):
    """ Export all known entity aliases to a CSV file. """
    export_aliases(path)


@manager.command
def index(entity_id=None):
    """ (Re-)create a full text search index. """
    if entity_id is not None:
        index_single(entity_id)
    else:
        index_entities()


@manager.command
def flush_index():
    """ Delete the full text search index. """
    flush_entities()


@manager.command
def sitemap(count=40000):
    """ Generate a static sitemap for SEO. """
    generate_sitemap(count=count)


@manager.command
def search(text):
    """ Search for a query string. """
    res = search_entities({'q': text})

    for hit in res:
        log.info("%s: %s", hit.get('_id'), hit.get('_source').get('name'))

    log.info("Total hits: %s", res.count())


if __name__ == "__main__":
    manager.run()
