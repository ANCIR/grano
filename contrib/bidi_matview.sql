

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

CREATE OR REPLACE FUNCTION refresh_grano_relation_bidi() RETURNS trigger AS
$$
BEGIN
    REFRESH MATERIALIZED VIEW grano_relation_bidi;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql ;

DROP TRIGGER IF EXISTS refresh_grano_relation_bidi ON grano_relation;

CREATE TRIGGER refresh_grano_relation_bidi AFTER TRUNCATE OR INSERT OR UPDATE OR DELETE
   ON grano_relation FOR EACH STATEMENT
   EXECUTE PROCEDURE refresh_grano_relation_bidi();
