import logging

from grano.model import Entity, Relation
from grano.logic.entities import _entity_changed
from grano.logic.relations import _relation_changed


log = logging.getLogger(__name__)


def rebuild():
    """ Execute the change processing handlers for all entities and
    relations currently loaded. This can be used as a housekeeping
    function. """

    for i, entity in enumerate(Entity.all().filter_by(same_as=None)):
        if i > 0 and i % 1000 == 0:
            log.info("Rebuilt: %s entities", i)
        _entity_changed(entity.id)

    for i, relation in enumerate(Relation.all()):
        if i > 0 and i % 1000 == 0:
            log.info("Rebuilt: %s relation", i)
        _relation_changed(relation.id)
