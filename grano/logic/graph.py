from StringIO import StringIO

from flask import request
from sqlalchemy import func, select, and_, not_
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

    def __init__(self, project_id=None, root_id=None):
        self.root_id = root_id
        self.project_id = project_id
        self._rows = []
        self._seen = set()
        self._rel_ids = set()
        self._G = None

        for i in range(self.depth):
            ids = self.sweep_ids()
            self.query_adjacency(sources=ids)
            self.query_adjacency(targets=ids)


    @property
    def depth(self):
        if self.root_id is None:
            return 1
        depth = arg_int('depth', 2)
        return max(1, min(depth, 3))


    @property
    def format(self):
        fmt = request.args.get('format', 'json').lower().strip()
        if fmt not in ['json', 'gexf']:
            raise BadRequest('Invalid format name: %s' % fmt)
        return fmt


    def query_adjacency(self, sources=None, targets=None):
        filters, fields = [], []

        relation = Relation.__table__.alias('relation')
        schema = Schema.__table__.alias('relation_schema')
        filters.append(relation.c.schema_id==schema.c.id)

        if len(self._rel_ids):
            filters.append(not_(relation.c.id.in_(self._rel_ids)))
        if self.project_id is not None:
            filters.append(relation.c.project_id==self.project_id)
        
        fields.append(relation.c.id.label('relation.id'))
        fields.append(schema.c.name.label('relation.schema.name'))
        fields.append(schema.c.label.label('relation.schema.label'))

        source_fields, source_filters, source_tables = \
            self.query_entity('source', sources)
        target_fields, target_filters, target_tables = \
            self.query_entity('target', targets)

        filters.append(relation.c.source_id==source_tables[0].c.id)
        filters.append(relation.c.target_id==target_tables[0].c.id)

        fields = fields + source_fields + target_fields
        filters = filters + source_filters + target_filters
        tables = [relation, schema] + source_tables + target_tables

        #print select(fields,  and_(*filters), tables)
        rp = db.session.execute(select(fields,  and_(*filters), tables))
        for row in rp.fetchall():
            self._rel_ids.add(row['relation.id'])
            self._rows.append(dict(row.items()))


    def query_entity(self, name, include):
        filters, fields = [], []
        table = Entity.__table__.alias(name)
        fields.append(table.c.id.label(name + '.id'))
        if include is not None:
            filters.append(table.c.id.in_(include))

        property_name = Property.__table__.alias(name + '_property_name')    
        filters.append(table.c.id==property_name.c.entity_id)
        filters.append(property_name.c.active==True)
        filters.append(property_name.c.name=='name')
        fields.append(property_name.c.value.label(name + '.property.name'))
        return (fields, filters, [table, property_name])


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


    def to_networkx(self):
        if self._G is None:
            G = nx.MultiDiGraph()
            for row in self._rows:
                if row.get('source.id') not in G:
                    G.add_node(row.get('source.id'), label=row.get('source.property.name'))
                if row.get('target.id') not in G:
                    G.add_node(row.get('target.id'), label=row.get('target.property.name'))
                G.add_edge(row.get('source.id'), row.get('target.id'), key=row.get('relation.id'),
                    schema_name=row.get('relation.schema.name'),
                    schema_label=row.get('relation.schema.label'))
            self._G = G
        return self._G


    def to_gexf(self):
        G = self.to_networkx()
        sio = StringIO()
        nx.write_gexf(G, sio)
        return sio.getvalue()


    def to_dict(self):
        relations, entities = [], {}
        for row in self._rows:
            relations.append({
                'id': row.get('relation.id'),
                'source': row.get('source.id'),
                'target': row.get('target.id'),
                'schema.name': row.get('relation.schema.name'),
                'schema.label': row.get('relation.schema.label'),
            })
            for ent in ['source', 'target']:
                if row.get(ent + '.id') not in entities:
                    entities[row.get(ent + '.id')] = {
                        #'id': row.get(ent + '.id'),
                        'property.name': row.get(ent + '.property.name')
                    }
        return {
            'relations': relations,
            'entities': entities,
            'root': self.root_id,
            'depth': self.depth
            }


if __name__ == '__main__':
    G = extract('783a709133447710b')
    nx.write_gexf(G, "graph.gexf")

