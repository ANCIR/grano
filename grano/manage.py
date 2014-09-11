import logging

from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand

from grano.views import app
from grano.model import Project
from grano.logic import import_schema, export_schema
from grano.logic import import_aliases, export_aliases
from grano.logic import rebuild as rebuild_
from grano.logic.accounts import console_account
from grano.logic.projects import save as save_project
from grano.plugins import list_plugins, notify_plugins
from grano.background import periodic as periodic_task


log = logging.getLogger('grano')
manager = Manager(app)
manager.add_command('db', MigrateCommand)
notify_plugins('grano.startup', lambda o: o.configure(manager))


@manager.command
def schema_import(project, path):
    """ Load a schema specification from a YAML file. """
    pobj = Project.by_slug(project)
    if pobj is None:
        pobj = save_project({
            'slug': project,
            'label': project,
            'author': console_account()
            })
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
    with open(path, 'w') as fh:
        export_aliases(pobj, fh)


@manager.command
def rebuild():
    """ Trigger change processing on all relations and entities. """
    rebuild_()


@manager.command
def periodic():
    """ Trigger the periodic background service. """
    periodic_task()


@manager.command
def adminkey():
    """ Print the API key for the system account. """
    print console_account().api_key


@manager.command
def plugins():
    """ List all available plugins. """
    for namespace, plugins in list_plugins().items():
        print "%s: %s" % (namespace, ' '.join(plugins))


def run():
    manager.run()

if __name__ == "__main__":
    run()
