import logging

from grano.core import celery as app
from grano.logic.entities import _entity_changed
from grano.logic.relations import _relation_changed
from grano.logic.imports import run_importer

log = logging.getLogger(__name__)


@app.task
def ping(message):
    log.warning("Ping was registered, message: %s", message)
