import logging
from datetime import datetime

from grano.core import db, celery
from grano.model import Pipeline, LogEntry
from grano.logic.accounts import console_account


def create(project, operation, label=None, config=None, author=None):
    """ Create a new pipeline object, in PENDING state. """
    pipeline = Pipeline()
    pipeline.status = Pipeline.STATUS_PENDING
    pipeline.project = project
    pipeline.label = label
    pipeline.operation = operation
    pipeline.percent_complete = 0
    pipeline.author = author or console_account()
    pipeline.config = config or {}
    db.session.add(pipeline)
    db.session.commit()
    return pipeline


def start(pipeline):
    """ Mark a given pipeline as running. """
    pipeline.status = Pipeline.STATUS_RUNNING
    pipeline.percent_complete = 0
    pipeline.started_at = datetime.utcnow()
    db.session.commit()


def finish(pipeline):
    """ Mark the given pipeline as complete or failed. """
    pipeline.percent_complete = 100
    if pipeline.has_errors():
        pipeline.status = Pipeline.STATUS_FAILED
    else:
        pipeline.status = Pipeline.STATUS_COMPLETE
    pipeline.ended_at = datetime.utcnow()
    db.session.commit()


def log(pipeline, level, message, error=None, details=None):
    """ Create a log entry related to the given pipeline. """
    entry = LogEntry()
    entry.pipeline = pipeline
    entry.level = level
    entry.message = message
    entry.error = error
    entry.details = details or {}
    db.session.add(entry)
    return entry


def log_debug(pipeline, message, error=None, details=None):
    return log(pipeline, logging.DEBUG, message, error=error, details=details)


def log_info(pipeline, message, error=None, details=None):
    return log(pipeline, logging.INFO, message, error=error, details=details)


def log_warn(pipeline, message, error=None, details=None):
    return log(pipeline, logging.WARNING, message, error=error, details=details)


def log_error(pipeline, message, error=None, details=None):
    return log(pipeline, logging.ERROR, message, error=error, details=details)
