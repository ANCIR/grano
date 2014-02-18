from sqlalchemy import func, select, and_
import networkx as nx

from grano.core import db
from grano.model import Entity, Relation, Schema, Property

entity_table = Entity.__table__
relation_table = Relation.__table__
schema_table = Schema.__table__
property_table = Property.__table__

# TODO: This should probably be two source files. 
# TODO: Make the set of properties retrieved for entities
#       and relations configurable. 
# TODO: Does it make sense to do a count first?
# TODO: Check what the last-modified entity/relation is.


def query(sources=None, targets=None):
    filters = []

    src = entity_table.alias('src')
    src_name = property_table.alias('srcname')
    if sources is not None:
        filters.append(src.c.id.in_(sources))
    filters.append(src.c.id==src_name.c.entity_id)
    filters.append(src_name.c.active==True)
    filters.append(src_name.c.name=='name')

    tar = entity_table.alias('tar')
    tar_name = property_table.alias('tarname')
    if targets is not None:
        filters.append(tar.c.id.in_(targets))
    filters.append(tar.c.id==tar_name.c.entity_id)
    filters.append(tar_name.c.active==True)
    filters.append(tar_name.c.name=='name')

    rel = relation_table.alias('rel')
    rel_schema = schema_table.alias('relschema')
    filters.append(rel.c.source_id==src.c.id)
    filters.append(rel.c.target_id==tar.c.id)
    filters.append(rel.c.schema_id==rel_schema.c.id)

    q = select([rel.c.id.label('rel_id'), rel_schema.c.name.label('rel_schema_name'),
                rel_schema.c.label.label('rel_schema_label'),
                src.c.id.label('src_id'), src_name.c.value.label('src_name'),
                tar.c.id.label('tar_id'), tar_name.c.value.label('tar_name')],
            and_(*filters), [rel, rel_schema, src, src_name])
    
    rows = []
    rp = db.session.execute(q)
    for row in rp.fetchall():
        rows.append(dict(row.items()))
    return rows


def extract_rec(root_id, depth):
    if depth <= 1:
        seen, rows = set(), []
    else:
        seen, rows = extract_rec(root_id, depth-1)

    ids = set()
    if len(rows):
        for row in rows:
            if row.get('src_id') not in seen:
                ids.add(row.get('src_id'))
                seen.add(row.get('src_id'))
            if row.get('tar_id') not in seen:
                ids.add(row.get('tar_id'))
                seen.add(row.get('tar_id'))
    else:
        ids.add(root_id)
        seen.add(root_id)
    
    rows = query(sources=ids)
    rows.extend(query(targets=ids))

    return seen, rows


def extract(root_id, depth=1):
    G = nx.MultiDiGraph()
    _, rows = extract_rec(root_id, depth)
    for row in rows:
        if row.get('src_id') not in G:
            G.add_node(row.get('src_id'), label=row.get('src_name'))
        if row.get('tar_id') not in G:
            G.add_node(row.get('tar_id'), label=row.get('tar_name'))
        G.add_edge(row.get('src_id'), row.get('tar_id'), key=row.get('rel_id'),
            name=row.get('rel_schema_name'),
            label=row.get('rel_schema_label'))
    return G


if __name__ == '__main__':
    G = extract('783a709133447710b')
    nx.write_gexf(G, "graph.gexf")

