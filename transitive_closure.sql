
WITH RECURSIVE search_graph(source_id, target_id, id, depth, path, cycle)
AS (
   SELECT e.source_id, e.target_id, e.id, 1,
          ARRAY[e.relation_id],
          false
   FROM grano_relation_bidi e

   UNION ALL

   SELECT e.source_id, e.target_id, e.id, sg.depth + 1,
          path || e.relation_id,
          e.relation_id = ANY(path)
   FROM grano_relation_bidi e, search_graph sg
   WHERE e.source_id = sg.target_id AND NOT cycle
)

SELECT DISTINCT source_id, target_id, depth, path FROM search_graph;
