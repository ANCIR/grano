from grano.core import db
from grano.interface import Periodic


COMPUTE_DEGREES = """
UPDATE grano_entity SET degree_in = 0;

UPDATE grano_entity SET degree_in = sq.cnt
    FROM
        (SELECT target_id, COUNT(r.id) AS cnt FROM grano_relation r
            GROUP BY r.target_id) AS sq
    WHERE grano_entity.id = sq.target_id;

UPDATE grano_entity SET degree_out = 0;

UPDATE grano_entity SET degree_out = sq.cnt
    FROM
        (SELECT source_id, COUNT(r.id) AS cnt FROM grano_relation r
            GROUP BY r.source_id) AS sq
    WHERE grano_entity.id = sq.source_id;

UPDATE grano_entity SET degree = degree_in + degree_out;
"""


class Degrees(Periodic):

    def run(self):
        db.session.execute(COMPUTE_DEGREES)
        db.session.commit()
