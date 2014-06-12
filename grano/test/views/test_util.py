import unittest
import flask
from grano import authz
from grano.views import util
from grano.core import db
from grano.model import Entity
from grano.test.test_authz import make_test_app, BaseAuthTestCase
from grano.test.test_authz import _project_and_permission
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest


class AllEntitiesTestCase(BaseAuthTestCase):

    def setUp(self):
        self.app = make_test_app()
        Entity.all().delete()
        # Consistently include an extra private project with Entity
        # that should not show in any test results
        project, permission = _project_and_permission(private=True)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity)

    def test_all_entities__private(self):
        project, permission = _project_and_permission(private=True)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertEqual(util.all_entities().count(), 0)

    def test_all_entities__private_reader_published(self):
        project, permission = _project_and_permission(
            reader=True, private=True)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertEqual(util.all_entities().count(), 1)

    def test_all_entities__private_reader_draft(self):
        project, permission = _project_and_permission(
            reader=True, private=True)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD-1)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertEqual(util.all_entities().count(), 0)

    def test_all_entities__private_editor_published(self):
        project, permission = _project_and_permission(
            editor=True, private=True)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertEqual(util.all_entities().count(), 1)

    def test_all_entities__private_editor_draft(self):
        project, permission = _project_and_permission(
            editor=True, private=True)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD-1)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertEqual(util.all_entities().count(), 1)

    def test_all_entities__not_private_published(self):
        project, permission = _project_and_permission(private=False)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertEqual(util.all_entities().count(), 1)

    def test_all_entities__not_private_draft(self):
        project, permission = _project_and_permission(
            reader=True, private=False)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD - 1)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            query = util.all_entities()
            self.assertEqual(util.all_entities().count(), 0)


class SingleArgTestCase(BaseAuthTestCase):

    def test_single_arg(self):
        d = MultiDict([('a', 'b')])
        self.assertEqual(util.single_arg(d, 'a'), 'b')

    def test_single_arg__bad_request(self):
        d = MultiDict([('a', 'b'), ('a', 'c')])
        with self.assertRaises(BadRequest):
            util.single_arg(d, 'a')

    def test_single_arg__allow_empty_duplicates(self):
        d = MultiDict([('a', 'b'), ('a', ' ')])
        self.assertEqual(util.single_arg(d, 'a'), 'b')
        

if __name__ == '__main__':
    unittest.main()
