from flask import request
from sqlalchemy import desc, asc


def parse_sorts():
    for key in request.args.getlist('sort'):
        direction = asc
        if key.startswith('-'):
            direction = desc
            key = key[1:]
        yield key, direction


def for_relations(q, Rel):
    for key, direction in parse_sorts():
        for cand in ['id', 'created_at', 'updated_at']:
            if key == cand:
                q = q.order_by(direction(getattr(Rel, key)))
        if key == 'source':
            q = q.order_by(direction(Rel.source_id, key))
        if key == 'target':
            q = q.order_by(direction(Rel.target_id, key))
    return q


def for_entities(q, Ent):
    for key, direction in parse_sorts():
        for cand in ['id', 'created_at', 'updated_at', 'degree', 'degree_in', 'degree_out']:
            if key == cand:
                q = q.order_by(direction(getattr(Ent, key)))
    return q
    
