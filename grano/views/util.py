from grano.model import Project


PROPERTY = 'property-'
ALIASES = 'aliases-'


def filter_query(cls, q, args):

    project = args.getlist('project')
    if len(project) and len(project[0].strip()):
        q = q.join(Project).filter(Project.slug==project[0])
    
    for key in args.keys():
        if key.startswith(PROPERTY):
            only_active = True
            prop = key[len(PROPERTY):]
            if prop.startswith(ALIASES):
                prop = prop[len(ALIASES):]
                only_active = False
            value = args.getlist(key)[0]
            q = cls._filter_property(q, prop, value,
                    only_active=only_active)

    return q
