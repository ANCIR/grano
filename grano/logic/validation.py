import re
import colander
from colander import Invalid

from grano.logic.references import ProjectRef
from grano.core import db
from grano.model import Schema, Attribute


FORBIDDEN = ['project', 'source', 'target', 'id', 'created_at', 'updated_at', 'author', 'author_id']
database_forbidden = colander.Function(lambda v: v not in FORBIDDEN, message="Reserved name")
database_format = colander.Regex('^[a-zA-Z][a-zA-Z0-9_]+[a-zA-Z0-9]$')
database_name = colander.All(database_format, database_forbidden)


class FixedValue(object):
    def __init__(self, value):
        self.value = value

    def serialize(self, node, appstruct):
        return colander.null

    def deserialize(self, node, cstruct):
        return self.value

    def cstruct_children(self, node, cstruct):
        return []
