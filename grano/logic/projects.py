from grano.core import app, db
from grano.model import Project


def save(slug, author, label=None, settings=None):
    """ Create or update a project with a given slug. """

    # TODO: sanitize the slug
    project = Project.by_slug(slug)
    if project is None:
        project = Project()
        project.slug = slug
        project.settings = {}

    if settings is not None:
        project.settings.update(settings)

    if label is not None:
        project.label = label

    if project.label is None:
        project.label = slug

    project.author = author
    db.session.add(project)
    
    from grano.service.schema import import_schema
    with app.open_resource('fixtures/base.yaml') as fh:
        import_schema(project, fh)

    db.session.flush()
    return project


def to_rest_index(project):
    return {
        'slug': project.slug,
        'label': project.label
    }


def to_rest(project):
    data = to_rest_index()
    data['settings'] = project.settings
    return data
