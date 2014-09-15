from grano.core import db
from grano.interface import Periodic, Startup


CREATE_VIEW = """
DROP MATERIALIZED VIEW IF EXISTS grano_relation_bidi;

CREATE MATERIALIZED VIEW grano_relation_bidi
    (created_at, updated_at, id, relation_id, schema_id, source_id, target_id, author_id, project_id, reverse)
    AS 
        SELECT created_at, updated_at, id AS id, id AS relation_id, schema_id, source_id,
            target_id, author_id, project_id, 'false'::boolean AS reverse FROM grano_relation
        UNION
        SELECT created_at, updated_at, CONCAT(id, ':rev') as id, id AS relation_id,
            schema_id, target_id AS source_id, source_id AS target_id,
            author_id, project_id, 'true'::boolean AS reverse FROM grano_relation
    WITH DATA;
"""

REFRESH_VIEW = """
    REFRESH MATERIALIZED VIEW grano_relation_bidi;
"""


class GenerateBidi(Periodic, Startup):

    def configure(self, manager):
        db.session.execute(CREATE_VIEW)
        db.session.commit()

    def run(self):
        db.session.execute(REFRESH_VIEW)
        db.session.commit()
