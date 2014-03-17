from grano.logic import Loader
import networkx

# This source URL will be applied to all properties without their own lineage:
DEFAULT_SOURCE_URL = 'https://dhs.stanford.edu/dh/gephi/dh11.gexf'

# Any settings (free-form dict):
PROJECT_SETTINGS = {}

def node_type(node):
    if node['type'] in ('Long Paper', 'Panel', 'Poster / Demo', 'Pre-Conference Tutorial', 'Pre-Conference Workshop', 'Short Paper'):
        return 'activity'
    else:
        return node['type']

def edge_type(source, target):
    ends = (node_type(source), node_type(target))
    if ends == ('person', 'university'):
        return 'affiliation'
    elif ends == ('person', 'activity'):
        return 'participation'
    else:
        raise

loader = Loader('dhs_stanford', project_label='opennews',
    project_settings=PROJECT_SETTINGS, source_url=DEFAULT_SOURCE_URL)

graph = networkx.gexf.read_gexf('dh11.gexf')

entities = {}

for node_id in graph.nodes():
    node = graph.node[node_id]

    node_schemata = ['category']
    if node_type(node) == 'activity':
        node_schemata.append('activity')
        entity = loader.make_entity(node_schemata)
        entity.set('type', node['type'])
    elif node_type(node) == 'university':
        node_schemata.append('university')
        entity = loader.make_entity(node_schemata)
        entity.set('latitude', float(node['xcoord']))
        entity.set('longitude', float(node['ycoord']))
    elif node_type(node) == 'person':
        node_schemata.append('person')
        entity = loader.make_entity(node_schemata)

    entity.set('category', node['category'])
    entity.set('name', node['label'])
    entity.save()
    entities[node_id] = entity

for src,tgt in graph.edges():
    et = edge_type(graph.node[src], graph.node[tgt])
    rel = loader.make_relation(et, entities[src], entities[tgt])
    rel.set('weight', 1)
    rel.save()

loader.persist()







# loader.persist()
