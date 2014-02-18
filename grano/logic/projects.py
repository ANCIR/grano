import colander

from grano.core import app, db, url_for
from grano.lib.exc import NotImplemented
from grano.logic.validation import database_name
from grano.logic.references import AccountRef
from grano.model import Project


class ProjectValidator(colander.MappingSchema):
    slug = colander.SchemaNode(colander.String(),
        validator=database_name)
    label = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3))
    author = colander.SchemaNode(AccountRef())
    settings = colander.SchemaNode(colander.Mapping(),
        missing={})


def save(data, project=None):
    """ Create or update a project with a given slug. """

    validator = ProjectValidator()
    data = validator.deserialize(data)

    if project is None:
        project = Project()
        project.slug = data.get('slug')

    project.settings = data.get('settings')
    project.label = data.get('label')
    project.author = data.get('author')

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


def to_rest(project):
    data = to_rest_index(project)
    data['settings'] = project.settings
    data['schemata_index_url'] = url_for('schemata_api.index', slug=project.slug)
    return data
