EXTRA_FIELDS = ['limit', 'offset', 'sort', 'optional', 'obj']


class ParserNode(object):
    """ A query parser object. This will help the query builder traverse
    the request and also fix up elements of the request that are
    ambiguous. """

    child_types = {}
    defaults = None
    key_field = None

    def __init__(self, project, name, source):
        self.project = project
        self.as_list = isinstance(source, (list, tuple))
        self._value = source
        if self.as_list:
            if len(source):
                self._value = source[0]
            else:
                self._value = None
        self.name = name

    @property
    def is_stub(self):
        if self._value is None:
            return True
        if not isinstance(self._value, dict):
            return False
        for k, v in self._value.items():
            if k not in EXTRA_FIELDS:
                return False
        return True

    @property
    def value(self):
        """ This will patch up the object with parsing defaults. """
        if self.is_stub:
            if self.defaults is None:
                return None
            self._value = {'*': None}

        # Transform: "foo" -> {"key": "foo"}
        if self.key_field and isinstance(self._value, basestring):
            self._value = {self.key_field: self._value}

        if isinstance(self._value, dict):

            # Expand wildcard queries
            if '*' in self._value:
                self._value.pop('*')
                for k, v in self.defaults.items():
                    if k not in self._value:
                        self._value[k] = v

            # Make sure ID is always fetched
            if 'id' not in self._value and self.name != 'properties':
                self._value['id'] = None
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def is_leaf(self):
        return not isinstance(self.value, dict)

    @property
    def children(self):
        if self.is_leaf:
            return
        for k, v in self.value.items():
            cls = self.child_types.get(None, ParserNode)
            cls = self.child_types.get(k, cls)
            yield cls(self.project, k, v)

    def to_dict(self):
        if self.is_leaf:
            return self.value
        else:
            data = dict([(c.name, c) for c in self.children])
            return [data] if self.as_list else data


class AccountParserNode(ParserNode):

    defaults = {
        'login': None
    }
    key_field = 'login'


class ProjectParserNode(ParserNode):

    defaults = {
        'slug': None,
        'label': None
    }
    key_field = 'slug'


class SchemaParserNode(ParserNode):

    defaults = {
        'name': None,
        'label': None,
        'hidden': None
    }
    key_field = 'name'


class PropertyParserNode(ParserNode):

    defaults = {
        'value': None,
        'source_url': None
    }
    key_field = 'value'


class PropertiesParserNode(ParserNode):

    defaults = {
        '*': None,
    }
    child_types = {
        None: PropertyParserNode
    }


class EntityParserNode(ParserNode):

    defaults = {
        'id': None,
        'degree': None,
        'schemata': [{}],
        'properties': {}
    }
    child_types = {
        'author': AccountParserNode,
        'project': ProjectParserNode,
        'schemata': SchemaParserNode,
        'schema': SchemaParserNode,
        'schema': SchemaParserNode,
        'properties': PropertiesParserNode
    }


class RelationParserNode(ParserNode):

    defaults = {
        'id': None,
        'reverse': None,
        'schema': [],
        'properties': {}
    }
    child_types = {
        'author': AccountParserNode,
        'project': ProjectParserNode,
        'schema': SchemaParserNode,
        'source': EntityParserNode,
        'other': EntityParserNode,
        'target': EntityParserNode,
        'properties': PropertiesParserNode
    }

EntityParserNode.child_types['inbound'] = RelationParserNode
EntityParserNode.child_types['outbound'] = RelationParserNode
EntityParserNode.child_types['relations'] = RelationParserNode
