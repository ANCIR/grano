import logging
from stevedore.enabled import EnabledExtensionManager

from grano.core import app


log = logging.getLogger(__name__)

NAMESPACES = [
    'grano.startup',
    'grano.entity.change',
    'grano.relation.change',
    'grano.schema.change',
    'grano.project.change'
]
PLUGINS = {'LOADED': False, 'MANAGERS': {}}


def _get_manager(namespace):
    enabled_plugins = app.config.get('PLUGINS', [])
    available_plugins = set()

    assert namespace in NAMESPACES, \
        '%s not one of %r' % (namespace, NAMESPACES)

    if not PLUGINS['LOADED']:

        for namespace_ in NAMESPACES:
            def check_func(ext):
                available_plugins.add(ext.name)
                return ext.name in enabled_plugins

            mgr = EnabledExtensionManager(
                namespace=namespace_,
                check_func=check_func,
                propagate_map_exceptions=False,
                invoke_on_load=True)
            PLUGINS['MANAGERS'][namespace_] = mgr

        PLUGINS['LOADED'] = True

        log.info("Enabled: %s", ", ".join(sorted(enabled_plugins)))
        log.info("Available: %s", ", ".join(sorted(available_plugins)))

    return PLUGINS['MANAGERS'][namespace]


def notify_plugins(namespace, callback):
    """ Notify all active plugins about an event in a given namespace.
    The second argument is a function, it'll be called once with each
    plugin instance which is available. """

    try:
        mgr = _get_manager(namespace)
        mgr.map(lambda ext, data: callback(ext.obj), None)
    except RuntimeError:
        pass


def list_plugins():
    """ List all available plugins, grouped by the namespace in which
    they're made available. """

    plugins = {}

    for namespace in NAMESPACES:
        plugins[namespace] = []
        mgr = _get_manager(namespace)
        try:
            mgr.map(lambda e, d: plugins[namespace].append(e.name), None)
        except RuntimeError:
            pass

    return plugins
