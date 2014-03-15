import abc


class EntityChangeProcessor(object):
    """ An entity change processor gets notified whenever there is a
    change to an entity so that it can perform related actions.

    This may happen out of band (ie. on a queue or batch job), thus 
    changes may not be applied immediately.
    """

    @abc.abstractmethod
    def entity_changed(self, entity_id):
        """ Notify the plugin that an entity has changed. The plugin 
        will only receive the ID and must query for the object itself. """


class RelationChangeProcessor(object):
    """ A relation change processor gets notified whenever there is a
    change to a relation so that it can perform related actions.

    This may happen out of band (ie. on a queue or batch job), thus 
    changes may not be applied immediately.
    """

    @abc.abstractmethod
    def relation_changed(self, relation_id):
        """ Notify the plugin that a relation has changed. The plugin 
        will only receive the ID and must query for the object itself. """


class Startup(object):
    """ This interface will be called when grano is started and allows
    plugins to register additional functionality such as flask views.
    """

    @abc.abstractmethod
    def configure(self, manager):
        """ Run this on startup. """

