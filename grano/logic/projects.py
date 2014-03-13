import colander
from datetime import datetime

from grano.core import app, db, url_for
from grano.lib.exc import NotImplemented
from grano.logic.validation import database_name
from grano.logic.references import AccountRef
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


def save(data, project=None):
    """ Create or update a project with a given slug. """

    data = validate(data, project)

    if project is None:
        project = Project()
        project.slug = data.get('slug')
        project.author = data.get('author')

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
    return project


def delete(project):
    raise NotImplemented()


def to_rest_index(project):
    return {
        'slug': project.slug,
        'label': project.label,
        'api_url': url_for('projects_api.view', slug=project.slug)
    }


def to_rest_index_stats(project):
    data = to_rest_index(project)
    data['entities_count'] = project.entities.count()
    data['relations_count'] = project.relations.count()
    return data


def to_rest(project):
    data = to_rest_index_stats(project)
    data['settings'] = project.settings
    data['author'] = accounts.to_rest_index(project.author)
    data['schemata_index_url'] = url_for('schemata_api.index', slug=project.slug)
    data['entities_index_url'] = url_for('entities_api.index', project=project.slug)
    data['relations_index_url'] = url_for('relations_api.index', project=project.slug)
    return data
