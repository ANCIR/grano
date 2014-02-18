from grano.model import Project


PROPERTY = 'property-'


def filter_query(cls, q, args):

    project = args.getlist('project')
    if len(project) and len(project[0].strip()):
        q = q.join(Project).filter(Project.slug==project[0])
    
    for key in args.keys():
        
        if key.startswith(PROPERTY):
            prop = key[len(PROPERTY):]
            value = args.getlist(key)[0]
            q = cls._filter_property(q, prop, value)

    return q
