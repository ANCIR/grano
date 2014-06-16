import colander
from colander import Invalid


class All(object):
    """ Composite validator which succeeds if none of its
    subvalidators raises an :class:`colander.Invalid` exception"""
    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, node, value):
        for validator in self.validators:
            validator(node, value)


FORBIDDEN = ['project', 'source', 'target', 'id', 'created_at', 'updated_at',
             'author', 'author_id']
database_format = colander.Regex(r'^[a-zA-Z][a-zA-Z0-9_-]+[a-zA-Z0-9]$')
database_forbidden = colander.Function(lambda t: t not in FORBIDDEN)
database_name = All(database_format, database_forbidden)


class FixedValue(object):
    def __init__(self, value):
        self.value = value

    def serialize(self, node, appstruct):
        return colander.null

    def deserialize(self, node, cstruct):
        return self.value

    def cstruct_children(self, node, cstruct):
        return []
