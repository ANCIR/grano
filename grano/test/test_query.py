import unittest

from grano.test.util import make_test_app
from grano.ql.query import run as query
from grano.ql.query import PARENT_ID


class TestQuery(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = make_test_app()

    def test_single_entity_id(self):
        res = query({'id': None}).to_dict()
        assert 'id' in res, res
        assert res['id'] is not None, res

    def test_list_entity_id(self):
        res = query([{'id': None}]).to_dict()
        assert len(res), res
        assert 'id' in res[0], res
        assert res[0]['id'] is not None, res

    def test_default_fields(self):
        res = query({'*': None}).to_dict()
        assert 'id' in res, res
        assert res['id'] is not None, res
        assert res['status'] is not None, res

    def test_author_nested(self):
        res = query({'author': None}).to_dict()
        assert 'author' in res, res
        assert res['author'] is not None, res
        assert res['author']['login'] is not None, res

    def test_author_filter(self):
        res = query({'author': {'login': '_system'}}).to_dict()
        assert 'author' in res, res
        assert res['author'] is not None, res
        assert res['author']['login'] == '_system', res

    def test_schema_nested(self):
        res = query({'schemata': None}).to_dict()
        assert 'schemata' in res, res
        assert res['schemata'] is not None, res
        assert res['schemata']['name'] is not None, res

    def test_schema_filter(self):
        res = query({'schemata': 'fellow'}).to_dict()
        assert 'schemata' in res, res
        assert res['schemata'] is not None, res
        assert res['schemata']['name'] == 'fellow', res

    def test_project_nested(self):
        res = query({'project': None}).to_dict()
        assert 'project' in res, res
        assert res['project'] is not None, res
        assert res['project']['slug'] is not None, res
        assert PARENT_ID not in res['project'], res

    def test_nested_relation_inbound(self):
        res = query({'inbound': {'id': None}}).to_dict()
        assert 'inbound' in res, res
        assert res['inbound'] is not None, res
        assert res['inbound']['id'] is not None, res

    def test_nested_relation_inbound_source(self):
        res = query({'inbound': {'id': None, 'source': None}}).to_dict()
        assert 'inbound' in res, res
        assert res['inbound'] is not None, res
        assert res['inbound']['id'] is not None, res
        assert res['inbound']['source']['id'] is not None, res

    def test_property_nested(self):
        res = query({'properties': {'name': None}}).to_dict()
        assert 'properties' in res, res
        assert res['properties'] is not None, res
        assert res['properties']['name'] is not None, res
        assert res['properties']['name']['source_url'] is not None, res
        assert res['properties']['name']['value'] is not None, res

    def test_property_filter(self):
        name = 'BBC'
        res = query({'properties': {'name': name}}).to_dict()
        assert 'properties' in res, res
        assert res['properties'] is not None, res
        assert res['properties']['name'] is not None, res
        assert res['properties']['name']['value'] == name, res

    def test_property_filter_none(self):
        name = 'Banana'
        res = query({'properties': {'name': name}}).to_dict()
        assert 'properties' in res, res
        assert res['id'] is None, res
        assert res['properties'] is not None, res
        assert res['properties']['name'] is not None, res

    def test_property_all(self):
        res = query({'properties': {'*': None}}).to_dict()
        assert 'properties' in res, res
        assert res['properties'] is not None, res
        assert '*' not in res['properties'], res
        assert res['properties']['name'] is not None, res

    def test_entity_all(self):
        res = query({'*': None}).to_dict()
        assert 'properties' in res, res
        assert res['properties'] is not None, res
        assert '*' not in res['properties'], res
        assert res['properties']['name'] is not None, res

if __name__ == '__main__':
    unittest.main()
