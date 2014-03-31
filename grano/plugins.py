from stevedore.enabled import EnabledExtensionManager

NAMESPACES = [
    'grano.startup',
    'grano.entity.change',
    'grano.relation.change',
    'grano.project.change'
    ]
MANAGERS = {}


def _get_manager(namespace):
    # TODO have an option in the config file to enable and 
    # disable plugins individually.
    assert namespace in NAMESPACES, '%s not one of %r' % (namespace, NAMESPACES)
    if namespace not in MANAGERS:
        mgr = EnabledExtensionManager(
            namespace=namespace,
            check_func=lambda x: True,
            propagate_map_exceptions=False,
            invoke_on_load=True)
        MANAGERS[namespace] = mgr
    return MANAGERS[namespace]


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
