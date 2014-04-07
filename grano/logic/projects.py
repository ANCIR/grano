import colander
from datetime import datetime

from grano.core import app, db, url_for, celery
from grano.lib.exc import NotImplemented
from grano.logic.validation import database_name
from grano.logic.references import AccountRef
from grano.plugins import notify_plugins
from grano.logic import accounts
from grano.model import Project


def validate(data, project):
    same_project = lambda s: Project.by_slug(s) == project
    same_project = colander.Function(same_project, message="Project exists")

    class ProjectValidator(colander.MappingSchema):
        slug = colander.SchemaNode(colander.String(),
            validator=colander.All(database_name, same_project))
        label = colander.SchemaNode(colander.String(),
            validator=colander.Length(min=3))
        private = colander.SchemaNode(colander.Boolean(),
            missing=False)
        author = colander.SchemaNode(AccountRef())
        settings = colander.SchemaNode(colander.Mapping(),
            missing={})

    validator = ProjectValidator()
    return validator.deserialize(data)


@celery.task
def _project_changed(project_slug, operation):
    """ Notify plugins about changes to a relation. """
    def _handle(obj):
        obj.project_changed(project_slug, operation)
    notify_plugins('grano.project.change', _handle)


def save(data, project=None):
    """ Create or update a project with a given slug. """

    data = validate(data, project)

    operation = 'create' if project is None else 'update'
    if project is None:
        project = Project()
        project.slug = data.get('slug')
        project.author = data.get('author')

        from grano.logic import permissions as permissions_logic
        permissions_logic.save({
            'account': data.get('author'),
            'project': project,
            'admin': True
            })

    project.settings = data.get('settings')
    project.label = data.get('label')
    project.private = data.get('private')
    project.updated_at = datetime.utcnow()
    
    db.session.add(project)
    
    # TODO: make this nicer - separate files? 
    from grano.logic.schemata import import_schema
    with app.open_resource('fixtures/base.yaml') as fh:
        import_schema(project, fh)

    db.session.flush()
    _project_changed(project.slug, operation)
    return project


def delete(project):
    """ Delete the project and all related data. """
    _project_changed(project.slug, 'delete')
    db.session.delete(project)
