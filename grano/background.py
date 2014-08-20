import logging

from grano.core import celery as app

log = logging.getLogger(__name__)


@app.task
def ping(message):
    log.warning("Ping was registered, message: %s", message)
