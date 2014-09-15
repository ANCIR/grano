from uuid import uuid4
from datetime import datetime

from sqlalchemy.sql.expression import select, func
from sqlalchemy import or_

from grano.core import db
from grano.model import Account, Schema, Entity, Property
from grano.model import BidiRelation
from grano.model.entity import entity_schema
from grano.query.parser import EXTRA_FIELDS, EntityParserNode


class Query(object):

    marker = None

    def __init__(self, parent, name, node):
        self.parent = parent
        self.node = node
        self.name = name
        self.results = {}
        if name is None:
            self.id = 'root'
        else:
            prefix = '_any' if name == '*' else name
            self.id = '%s_%s' % (prefix, uuid4().hex[:10])

    def join(self, from_obj, partial=False):
        return from_obj

    def query(self, parent_ids=None):
        pass

    def get_child_node_value(self, name, default=None):
        for node in self.node.children:
            if node.name == name:
                return node.value
        return default

    @property
    def optional(self):
        if self.parent is not None and self.parent.optional:
            return True
        if self.get_child_node_value('optional', False):
            return True
        return False


class FieldQuery(Query):
    """ Query a simple field, as opposed to a more complex nested
    object. """
    
    def __init__(self, parent, name, node):
        super(FieldQuery, self).__init__(parent, name, node)

    @property
    def filtered(self):
        return self.node.value is not None

    @property
    def column(self):
        return getattr(self.parent.alias.c, self.name)

    def filter(self, q, partial=False):
        if self.filtered:
            cond = self.column == self.node.value
            if self.optional:
                cond = or_(cond, self.column==None)
            q = q.where(cond)
        return q

    def project(self, q):
        if self.name == 'id' or not self.filtered:
            q = q.column(self.column.label(self.id))
        return q

    def collect(self, row):
        if self.filtered:
            val = self.node.value
        else:
            val = row.get(self.id, None)
        self.results[row.get(self.parent.pk_id)] = val

    def assemble(self, parent_id):
        return self.results.get(parent_id)


class ObjectQuery(Query):

    model = {}
    domain_object = None
    
    def __init__(self, parent, name, node):
        super(ObjectQuery, self).__init__(parent, name, node)
        self.children = {}
        self.alias = self.domain_object.__table__.alias(self.id)

        # instantiate the model:
        for name, cls in self.model.items():
            for node in self.node.children:
                if node.name == name:
                    self.children[name] = cls(self, name, node)

    @property
    def pk_id(self):
        for name, child in self.children.items():
            if name == 'id':
                return child.id

    @property
    def filtered(self):
        for child in self.node.children:
            if child.name in EXTRA_FIELDS:
                continue
            if self.children[child.name].filtered:
                return True

    def join(self, from_obj, partial=False):
        """ Apply the joins specified on this level of the query. """
        if partial and not self.filtered:
            return from_obj

        if self.parent:
            from_obj = self.join_parent(from_obj)

        for child in self.node.children:
            if child.name in EXTRA_FIELDS:
                continue
            if child.name in self.children:
                field = self.children[child.name]
                from_obj = field.join(from_obj, partial=True)
        return from_obj

    def filter(self, q, partial=False):
        """ Apply the joins specified on this level of the query. """
        if not self.filtered:
            return q

        for child in self.node.children:
            if child.name in EXTRA_FIELDS:
                continue
            if child.name in self.children:
                field = self.children[child.name]
                q = field.filter(q, partial=partial)
        return q

    def join_parent(self, from_obj):
        return from_obj

    def project(self, q):
        """ Define the columns to be retrieved when this is the active
        level of the query. """
        if self.parent is not None:
            q = q.column(self.parent.alias.c.id.label(self.parent.pk_id))

        for name, child in self.children.items():
            for node in self.node.children:
                if not node.name == name:
                    continue
                if isinstance(child, FieldQuery):
                    q = child.project(q)
        return q

    def query(self, parent_ids=None):
        """ Construct a SQL query for this level of the request. """
        if self.parent is None:
            q = select(from_obj=self.join(self.alias))
            q = q.offset(self.get_child_node_value('offset', 0))
            if not self.node.as_list:
                q = q.limit(1)
            else:
                q = q.limit(self.get_child_node_value('limit', 10))
        else:
            q = select(from_obj=self.join(self.parent.alias))
        q = self.filter(q)
        
        if parent_ids is not None:
            q = q.where(self.parent.alias.c.id.in_(parent_ids))
        
        q = self.project(q)
        q = q.distinct()
        #print self, type(self)
        #print q

        ids = []
        rp = db.session.execute(q)
        while True:
            row = rp.fetchone()
            if row is None:
                break
            row = dict(row.items())
            ids.append(row.get(self.pk_id))
            self.collect(row)

        for name, child in self.children.items():
            child.query(parent_ids=ids)

    def count(self):
        """ Get a count of the number of distinct objects. """
        q = select(from_obj=self.join(self.alias))
        q = self.filter(q, partial=True)
        q = q.column(func.count(func.distinct(self.alias.c.id)).label('num'))
        rp = db.session.execute(q)
        return rp.fetchone().num

    def collect(self, row):
        parent_id = row.get(self.parent.pk_id) if self.parent else None
        if parent_id not in self.results:
            self.results[parent_id] = {}
        id = row.get(self.pk_id)
        if id not in self.results[parent_id]:
            data = {}
            if self.marker is not None:
                data['obj'] = self.marker
            self.results[parent_id][id] = data

        for name, child in self.children.items():
            if isinstance(child, FieldQuery):
                child.collect(row)

    def assemble(self, parent_id):
        data = self.results.get(parent_id, {})
        items = []
        for id, item in data.items():
            for name, child in self.children.items():
                item[name] = child.assemble(id)
            items.append(item)

            if not self.node.as_list:
                break

        if not self.node.as_list and len(items):
            return items.pop()
        return items

    def run(self):
        self.query()
        return self.assemble(None)


class IdFieldQuery(FieldQuery):

    def assemble(self, parent_id):
        id = super(IdFieldQuery, self).assemble(parent_id)
        return id.split(':', 1)[0]


class AuthorQuery(ObjectQuery):
    
    domain_object = Account
    model = {
        'id': FieldQuery,
        'login': FieldQuery,
        'full_name': FieldQuery,
        'created_at': FieldQuery,
        'updated_at': FieldQuery
    }

    def join_parent(self, from_obj):
        return from_obj.join(self.alias,
                             onclause=self.alias.c.id == self.parent.alias.c.author_id,
                             isouter=self.optional)


class SchemaQuery(ObjectQuery):
    
    domain_object = Schema
    model = {
        'id': FieldQuery,
        'name': FieldQuery,
        'hidden': FieldQuery,
        'label': FieldQuery,
        'created_at': FieldQuery,
        'updated_at': FieldQuery
    }

    def join_parent(self, from_obj):
        return from_obj.join(self.alias,
                             onclause=self.alias.c.id == self.parent.alias.c.schema_id,
                             isouter=self.optional)


class SchemataQuery(SchemaQuery):

    def join_parent(self, from_obj):
        jt = entity_schema.alias()
        from_obj = from_obj.join(jt, self.parent.alias.c.id == jt.c.entity_id,
                                 isouter=self.optional)
        return from_obj.join(self.alias,
                             onclause=self.alias.c.id == jt.c.schema_id,
                             isouter=self.optional)


class PropertyQuery(ObjectQuery):
    """ Property queries are the second level in querying a set of
    properties, they are called by the PropertiesQuery. This is somewhat
    complex because we need to handle types (i.e. query the appropriate
    column for the submitted input type, or retrieve all to find the
    one that holds a value. """

    domain_object = Property
    value_columns = {
        'value_string': basestring,
        'value_datetime': datetime,
        'value_integer': int,
        'value_float': float,
        'value_boolean': bool
    }
    model = {
        'id': FieldQuery,
        'name': FieldQuery,
        'value_string': FieldQuery,
        'value_datetime': FieldQuery,
        'value_integer': FieldQuery,
        'value_float': FieldQuery,
        'value_boolean': FieldQuery,
        'source_url': FieldQuery,
        'active': FieldQuery
    }

    def __init__(self, parent, name, node):
        if 'value' in node.value:
            obj = node.value.pop('value')
            if obj is None:
                for col in self.value_columns:
                    node.value[col] = None
            else:
                for col, type_ in self.value_columns.items():
                    if isinstance(obj, type_):
                        node.value[col] = obj

        if name == '*':
            node.value['name'] = None
        else:
            node.value['name'] = name
        node.value['active'] = True
        node.value['optional'] = True
        node.as_list = True
        super(PropertyQuery, self).__init__(parent, name, node)

    def filter(self, q, partial=False):
        for child in self.node.children:
            if child.name in EXTRA_FIELDS:
                continue
            if child.name in self.children:
                field = self.children[child.name]
                q = field.filter(q, partial=partial)
        return q

    @property
    def filtered(self):
        for name, child in self.children.items():
            if child.filtered:
                if name in self.value_columns:
                    return True
            #if name == 'name' and child.filtered:
            #    return True
        return False

    def assemble(self, parent_id):
        props = {}
        for prop in super(PropertyQuery, self).assemble(parent_id):
            prop['value'] = None
            for col in self.value_columns:
                col_val = prop.pop(col, None)
                if col_val is not None:
                    prop['value'] = col_val
            props[prop.pop('name')] = prop
        return props


class EntityPropertyQuery(PropertyQuery):

    def join_parent(self, from_obj):
        return from_obj.join(self.alias,
                             onclause=self.alias.c.entity_id == self.parent.alias.c.id,
                             isouter=self.optional)


class RelationPropertyQuery(PropertyQuery):

    def join_parent(self, from_obj):
        return from_obj.join(self.alias,
                             onclause=self.alias.c.relation_id == self.parent.alias.c.relation_id,
                             isouter=self.optional)


class PropertiesQuery(object):
    """ A stub query object to retrieve all the requested properties
    and return them in an associative array. """

    def __init__(self, parent, name, node):
        self.parent = parent
        self.children = []
        for child in node.children:
            prop = self.child_cls(parent, child.name, child)
            self.children.append(prop)

    @property
    def filtered(self):
        for child in self.children:
            if child.filtered:
                return True
        return False

    def filter(self, q, partial=False):
        for child in self.children:
            if child.filtered:
                q = child.filter(q, partial=partial)
        return q

    def join(self, from_obj, partial=False):
        for child in self.children:
            from_obj = child.join(from_obj, partial=partial)
        return from_obj

    def query(self, parent_ids=None):
        for child in self.children:
            child.query(parent_ids=parent_ids)

    def collect(self, row):
        for child in self.children:
            child.collect(row)

    def assemble(self, parent_id):
        data = {}
        for child in self.children:
            data.update(child.assemble(parent_id))
        return data

    @property
    def optional(self):
        return True


class EntityPropertiesQuery(PropertiesQuery):
    child_cls = EntityPropertyQuery


class RelationPropertiesQuery(PropertiesQuery):
    child_cls = RelationPropertyQuery


class RelationQuery(ObjectQuery):
    
    domain_object = BidiRelation
    marker = 'relation'
    model = {
        'id': IdFieldQuery,
        'reverse': FieldQuery,
        'author': AuthorQuery,
        'schema': SchemaQuery,
        'properties': RelationPropertiesQuery,
        'created_at': FieldQuery,
        'updated_at': FieldQuery
    }

    @property
    def filtered(self):
        return True

    def bidi_filter(self, q):
        return q.where(self.alias.c.reverse == False) # noqa

    def filter(self, q, partial=False):
        if self.filtered or not partial:
            q = q.where(self.alias.c.project_id == self.node.project.id)
            q = self.bidi_filter(q)
        return super(RelationQuery, self).filter(q, partial=partial)


class InboundRelationQuery(RelationQuery):

    def join_parent(self, from_obj):
        return from_obj.join(self.alias,
                             onclause=self.alias.c.target_id == self.parent.alias.c.id,
                             isouter=self.optional)


class OutboundRelationQuery(RelationQuery):

    def join_parent(self, from_obj):
        return from_obj.join(self.alias,
                             onclause=self.alias.c.source_id == self.parent.alias.c.id,
                             isouter=self.optional)


class BidiRelationQuery(RelationQuery):

    def bidi_filter(self, q):
        return q

    def join_parent(self, from_obj):
        return from_obj.join(self.alias,
                             onclause=self.alias.c.target_id == self.parent.alias.c.id,
                             isouter=self.optional)


class EntityQuery(ObjectQuery):
    
    domain_object = Entity
    marker = 'entity'
    model = {
        'id': FieldQuery,
        'created_at': FieldQuery,
        'updated_at': FieldQuery,
        'degree_in': FieldQuery,
        'degree_out': FieldQuery,
        'degree': FieldQuery,
        'schemata': SchemataQuery,
        'schema': SchemaQuery,
        'author': AuthorQuery,
        'inbound': InboundRelationQuery,
        'outbound': OutboundRelationQuery,
        'relations': BidiRelationQuery,
        'properties': EntityPropertiesQuery,
    }

    @property
    def filtered(self):
        return True

    def filter(self, q, partial=False):
        if self.filtered or not partial or not self.parent:
            q = q.where(self.alias.c.project_id == self.node.project.id)
            q = q.where(self.alias.c.same_as == None) # noqa
        return super(EntityQuery, self).filter(q, partial=partial)


class SourceEntityQuery(EntityQuery):

    def join_parent(self, from_obj):
        return from_obj.join(self.alias,
                             onclause=self.alias.c.id == self.parent.alias.c.source_id,
                             isouter=self.optional)


class TargetEntityQuery(EntityQuery):

    def join_parent(self, from_obj):
        return from_obj.join(self.alias,
                             onclause=self.alias.c.id == self.parent.alias.c.target_id,
                             isouter=self.optional)


class BidiEntityQuery(EntityQuery):

    def join_parent(self, from_obj):
        return from_obj.join(self.alias,
                             onclause=self.alias.c.id == self.parent.alias.c.source_id,
                             isouter=self.optional)


InboundRelationQuery.model['source'] = SourceEntityQuery
OutboundRelationQuery.model['target'] = TargetEntityQuery
BidiRelationQuery.model['other'] = BidiEntityQuery


def run_query(project, query):
    node = EntityParserNode(project, None, query)
    node.value['limit'] = min(1000, node.value.get('limit', 25))
    node.value['offset'] = max(0, node.value.get('offset', 0))
    eq = EntityQuery(None, None, node)
    return eq
