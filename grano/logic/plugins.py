import logging

from grano.model import Entity, Relation, Project
from grano.logic.entities import _entity_changed
from grano.logic.relations import _relation_changed
from grano.logic.projects import _project_changed
from grano.logic.schemata import _schema_changed


log = logging.getLogger(__name__)


def rebuild():
    """ Execute the change processing handlers for all entities and
    relations currently loaded. This can be used as a housekeeping
    function. """

    for project in Project.all():
        _project_changed(project.slug, 'delete')
        _project_changed(project.slug, 'create')

        for schema in project.schemata:
            _schema_changed(schema.project.slug, schema.name, 'delete')
            _schema_changed(schema.project.slug, schema.name, 'create')

        eq = Entity.all().filter_by(same_as=None)
        eq = eq.filter_by(project=project)
        for i, entity in enumerate(eq):
            if i > 0 and i % 1000 == 0:
                log.info("Rebuilt: %s entities", i)
            _entity_changed(entity.id, 'delete')
            _entity_changed(entity.id, 'create')

        rq = Relation.all().filter_by(project=project)
        for i, relation in enumerate(rq):
            if i > 0 and i % 1000 == 0:
                log.info("Rebuilt: %s relation", i)
            _relation_changed(relation.id, 'delete')
            _relation_changed(relation.id, 'create')
