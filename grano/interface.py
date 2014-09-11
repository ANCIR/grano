import abc


class EntityChangeProcessor(object):
    """ An entity change processor gets notified whenever there is a
    change to an entity so that it can perform related actions.

    This may happen out of band (ie. on a queue or batch job), thus
    changes may not be applied immediately.
    """

    @abc.abstractmethod
    def entity_changed(self, entity_id, operation):
        """ Notify the plugin that an entity has changed. The plugin
        will only receive the ID and must query for the object itself. """


class RelationChangeProcessor(object):
    """ A relation change processor gets notified whenever there is a
    change to a relation so that it can perform related actions.

    This may happen out of band (ie. on a queue or batch job), thus
    changes may not be applied immediately.
    """

    @abc.abstractmethod
    def relation_changed(self, relation_id, operation):
        """ Notify the plugin that a relation has changed. The plugin
        will only receive the ID and must query for the object itself. """


class ProjectChangeProcessor(object):
    """ A project change processor gets notified whenever there is a
    change to a project's settings so that it can perform related actions.

    This may happen out of band (ie. on a queue or batch job), thus
    changes may not be applied immediately.
    """

    @abc.abstractmethod
    def project_changed(self, project_slug, operation):
        """ Notify the plugin that a project has changed. The plugin
        will only receive the ID and must query for the object itself. """


class SchemaChangeProcessor(object):
    """ A schema change processor gets notified whenever there is a
    change to a schema definition so that it can perform related actions.

    This may happen out of band (ie. on a queue or batch job), thus
    changes may not be applied immediately.
    """

    @abc.abstractmethod
    def schema_changed(self, project_slug, schema_name, operation):
        """ Notify the plugin that a project has changed. The plugin
        will only receive the ID and must query for the object itself. """


class Startup(object):
    """ This interface will be called when grano is started and allows
    plugins to register additional functionality such as flask views.
    """

    @abc.abstractmethod
    def configure(self, manager):
        """ Run this on startup. """


class Periodic(object):
    """ This interface will be called periodically, to execute house
    keeping jobs. The exact period is up to the type of deployment.
    """

    @abc.abstractmethod
    def run(self):
        """ Run an action. """
