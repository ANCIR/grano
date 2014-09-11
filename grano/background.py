import logging

from grano.core import celery as app
from grano.plugins import notify_plugins


log = logging.getLogger(__name__)


@app.task
def ping(message):
    log.warning("Ping was registered, message: %s", message)


@app.task
def periodic():
    def _handle(obj):
        obj.run()
    notify_plugins('grano.periodic', _handle)
