import logging 

from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

from grano.core import db, assets
from grano.views import app
from grano.model import Project
from grano.service import import_schema, export_schema
from grano.service import import_aliases, export_aliases
from grano.service import index_entities, index_single
from grano.service import flush_entities, rebuild as rebuild_
from grano.logic.searcher import search_entities
from grano.logic.accounts import console_account
from grano.logic.projects import save as ensure_project
from grano.service import generate_sitemap
from grano.plugins import list_plugins


log = logging.getLogger('grano')
manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))


@manager.command
def createdb():
    """ Create the database schema. """
    db.create_all()


@manager.command
def schema_import(project, path):
    """ Load a schema specification from a YAML file. """
    pobj = ensure_project(project, console_account())
    with open(path, 'r') as fh:
        import_schema(pobj, fh)


@manager.command
def schema_export(project, path):
    """ Export the current schema to a YAML file. """
    pobj = Project.by_slug(project)
    assert pobj is not None, 'Project not available: %s' % project
    export_schema(pobj, path)


@manager.command
def alias_import(project, path):
    """ Load a set of entity aliases from a CSV file. """
    pobj = Project.by_slug(project)
    assert pobj is not None, 'Project not available: %s' % project
    import_aliases(pobj, console_account(), path)


@manager.command
def alias_export(project, path):
    """ Export all known entity aliases to a CSV file. """
    pobj = Project.by_slug(project)
    assert pobj is not None, 'Project not available: %s' % project
    export_aliases(pobj, path)


@manager.command
def index(entity_id=None):
    """ (Re-)create a full text search index. """
    if entity_id is not None:
        index_single(entity_id)
    else:
        index_entities()


@manager.command
def rebuild():
    """ Trigger change processing on all relations and entities. """
    rebuild_()


@manager.command
def flush_index():
    """ Delete the full text search index. """
    flush_entities()


@manager.command
def plugins():
    """ List all available plugins. """
    for namespace, plugins in list_plugins().items():
        print "%s: %s" % (namespace, ' '.join(plugins)) 


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


def run():
    manager.run()

if __name__ == "__main__":
    run()    
