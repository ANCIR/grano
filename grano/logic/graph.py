from StringIO import StringIO
from hashlib import sha1

from flask import request
from sqlalchemy import select, and_, not_
import networkx as nx

from grano.lib.exc import BadRequest
from grano.lib.args import arg_int
from grano.core import db
from grano.model import Entity, Relation, Schema, Property


# TODO: Make the set of properties retrieved for entities
#       and relations configurable.
# TODO: Does it make sense to do a count first?
# TODO: Check what the last-modified entity/relation is.
# TODO: Possibly aggregate relations with the same props
#       into a weight.


class GraphExtractor(object):

    def __init__(self, project_id=None, root_id=None, entity_properties=None):
        self.root_id = root_id
        self.project_id = project_id
        self.entity_properties = []
        if entity_properties is not None:
            self.entity_properties = entity_properties

        self._rows = None
        self._seen = set()
        self._entities = set()
        self._rel_ids = set()
        self._G = None

    @property
    def depth(self):
        if self.root_id is None:
            return 1
        depth = arg_int('depth', 1)
        return max(1, min(depth, 3))

    @property
    def format(self):
        fmt = request.args.get('format', 'json').lower().strip()
        if fmt not in ['json', 'gexf']:
            raise BadRequest('Invalid format name: %s' % fmt)
        return fmt

    def query(self):
        self._rows = []
        for i in range(self.depth):
            ids = self.sweep_ids()
            self.query_adjacency(sources=ids)
            self.query_adjacency(targets=ids)
        return self._rows

    def query_adjacency(self, sources=None, targets=None):
        filters, fields = [], []

        relation = Relation.__table__.alias('relation')
        schema = Schema.__table__.alias('relation_schema')
        filters.append(relation.c.schema_id == schema.c.id)

        if len(self._rel_ids):
            filters.append(not_(relation.c.id.in_(self._rel_ids)))
        if self.project_id is not None:
            filters.append(relation.c.project_id == self.project_id)

        fields.append(relation.c.id.label('relation.id'))
        fields.append(relation.c.source_id.label('source.id'))
        fields.append(relation.c.target_id.label('target.id'))
        fields.append(schema.c.name.label('relation.schema.name'))
        fields.append(schema.c.label.label('relation.schema.label'))

        if sources is not None:
            filters.append(relation.c.source_id.in_(sources))

        if targets is not None:
            filters.append(relation.c.target_id.in_(targets))

        tables = [relation, schema]

        rp = db.session.execute(select(fields, and_(*filters), tables))
        for row in rp.fetchall():
            self._rows.append(dict(row.items()))
            self._entities.add(row['source.id'])
            self._entities.add(row['target.id'])
            self._rel_ids.add(row['relation.id'])

    def query_entities(self, entity_ids=None):
        if entity_ids is None:
            entity_ids = self._entities
        q = db.session.query(Entity.id)
        q = q.filter(Entity.id.in_(entity_ids))
        q = q.join(Schema, Entity.schemata)
        q = q.join(Property, Entity.properties)
        q = q.filter(Property.name == 'name')
        q = q.filter(Property.active == True)  # noqa

        q = q.add_columns(
            Property.value_string.label('name'),
            Schema.name.label('schema')
        )
        entities = {}
        for id_, name, schema in q.all():
            entities.setdefault(id_, {'property.name': name, 'schemata': []})
            entities[id_]['schemata'].append(schema)

        if self.entity_properties:
            q = db.session.query(Property)
            q = q.filter(Property.entity_id.in_(entity_ids))
            q = q.filter(Property.name.in_(self.entity_properties))
            q = q.filter(Property.active == True)  # noqa
            for row in q.all():
                entities[row.entity_id]['property.' + row.name] = row.value

        return entities

    def sweep_ids(self):
        if self.root_id is None:
            return None
        if not len(self._rows):
            ids = set([self.root_id])
        else:
            ids = set()
            for row in self._rows:
                for field in ['source.id', 'target.id']:
                    if row.get(field) not in self._seen:
                        ids.add(row.get(field))
        self.seen = self._seen.union(ids)
        return ids

    def to_hash(self):
        if self._rows is None:
            self.query()
        hasch = sha1()
        for row in self._rows:
            hasch.update(row.get('source.id'))
            hasch.update(row.get('target.id'))
            hasch.update(row.get('relation.id'))
        return hasch.hexdigest()

    def to_networkx(self):
        if self._G is None:
            if self._rows is None:
                self.query()
                entities = self.query_entities()
            G = nx.MultiDiGraph()
            for row in self._rows:
                if row.get('source.id') not in G:
                    entity = entities[row.get('source.id')]
                    G.add_node(row.get('source.id'),
                        attr_dict={'schemata': ','.join(entity['schemata'])},
                        label=entity['property.name'])
                if row.get('target.id') not in G:
                    entity = entities[row.get('target.id')]
                    G.add_node(row.get('target.id'),
                        attr_dict={'schemata': ','.join(entity['schemata'])},
                        label=entity['property.name'])
                G.add_edge(row.get('source.id'), row.get('target.id'),
                           key=row.get('relation.id'),
                           schema_name=row.get('relation.schema.name'),
                           schema_label=row.get('relation.schema.label')
                )
            self._G = G
        return self._G

    def to_gexf(self):
        G = self.to_networkx()
        sio = StringIO()
        nx.write_gexf(G, sio)
        return sio.getvalue()

    def to_dict(self):
        if self._rows is None:
            self.query()
        entities = self.query_entities()
        relations = []
        for row in self._rows:
            relations.append({
                'id': row.get('relation.id'),
                'source': row.get('source.id'),
                'target': row.get('target.id'),
                'schema.name': row.get('relation.schema.name'),
                'schema.label': row.get('relation.schema.label'),
            })

        return {
            'relations': relations,
            'entities': entities,
            'root': self.root_id,
            'depth': self.depth
        }
