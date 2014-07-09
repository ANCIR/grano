import unittest
import flask
from grano import authz
from grano import core
from grano.core import db
from grano.manage import app
from grano.model import Project, Permission, Entity, Relation
from grano.test.fixtures import create_fixtures


def make_test_app(use_cookies=False):
    """For some reason this does not work when imported from util.
    Error is:
        AttributeError: 'FlaskClient' object has no attribute 'test_request_context'
    """
    app.config['TESTING'] = True
    app.config['CACHE'] = False
    app.config['PLUGINS'] = []
    app.config['CELERY_ALWAYS_EAGER'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.create_all()
    create_fixtures()
    return app


class BaseAuthTestCase(unittest.TestCase):
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)
    
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)


def _project_and_permission(
        private=False,
        reader=False,
        editor=False,
        admin=False, account_id=1):
    project = Project(private=private)
    db.session.add(project)
    db.session.commit()
    perm = Permission(account_id=account_id, project_id=project.id,
        reader=reader, editor=editor, admin=admin)
    db.session.add(perm)
    db.session.commit()
    return project, perm


class ProjectAuthTestCase(BaseAuthTestCase):

    def setUp(self):
        self.app = make_test_app()

    def test_public_project_read(self):
        project, permission = _project_and_permission()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertTrue(authz.project_read(project))

    def test_private_project_read__no_perm(self):
        project, permission = _project_and_permission(private=True)
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertFalse(authz.project_read(project))
      
    def test_private_project_read__admin_only(self):
        """Perms are designed such that admin/editor cannot read private
        projects unless they have explicit read permission."""
        project, permission = _project_and_permission(
            private=True, admin=True)
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertFalse(authz.project_read(project))
      
    def test_private_project_read__editor_only(self):
        project, permission = _project_and_permission(
            private=True, editor=True)
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertFalse(authz.project_read(project))
      
    def test_private_project_read__reader_only(self):
        with self.app.test_request_context():
            project, permission = _project_and_permission(
                private=True, reader=True)
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertTrue(authz.project_read(project))
      
        
class EntityAuthTestCase(BaseAuthTestCase):

    def setUp(self):
        self.app = make_test_app()

    def test_public_project_entity_read__default_status(self):
        project, permission = _project_and_permission()
        entity = Entity(project=project)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertFalse(authz.entity_read(entity))

    def test_public_project_entity_read__publish_status(self):
        project, permission = _project_and_permission()
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertTrue(authz.entity_read(entity))

    def test_public_project_entity_read__draft_status(self):
        project, permission = _project_and_permission()
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD-1)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertFalse(authz.entity_read(entity))

    def test_private_project_entity_read__publish_status_reader(self):
        project, permission = _project_and_permission(private=True,
            reader=True)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertTrue(authz.entity_read(entity))

    def test_private_project_entity_read__draft_status_reader(self):
        project, permission = _project_and_permission(private=True,
            reader=True)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD-1)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertFalse(authz.entity_read(entity))

    def test_private_project_entity_read__draft_status_editor(self):
        project, permission = _project_and_permission(private=True,
            editor=True)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD-1)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertTrue(authz.entity_read(entity))

    def test_private_project_entity_read__draft_status_admin(self):
        project, permission = _project_and_permission(private=True,
            admin=True)
        entity = Entity(project=project, status=authz.PUBLISHED_THRESHOLD-1)
        db.session.add(entity)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertTrue(authz.entity_read(entity))

class RelationAuthTestCase(BaseAuthTestCase):

    def setUp(self):
        self.app = make_test_app()

    def test_entity_read__unreadable(self):
        project, permission = _project_and_permission()
        entity_source = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD-1)
        entity_target = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD-1)
        db.session.add(entity_source)
        db.session.add(entity_target)
        rel = Relation(source=entity_source, target=entity_target)
        db.session.add(rel)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertFalse(authz.relation_read(rel))

    def test_entity_read__readable(self):
        project, permission = _project_and_permission()
        entity_source = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        entity_target = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity_source)
        db.session.add(entity_target)
        rel = Relation(source=entity_source, target=entity_target)
        db.session.add(rel)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertTrue(authz.relation_read(rel))

    def test_entity_edit__editable(self):
        project, permission = _project_and_permission(editor=True)
        entity_source = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        entity_target = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity_source)
        db.session.add(entity_target)
        rel = Relation(source=entity_source, target=entity_target)
        db.session.add(rel)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertTrue(authz.relation_edit(rel))

    def test_entity_edit__uneditable(self):
        project, permission = _project_and_permission(editor=False)
        entity_source = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        entity_target = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity_source)
        db.session.add(entity_target)
        rel = Relation(source=entity_source, target=entity_target)
        db.session.add(rel)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertFalse(authz.relation_edit(rel))

    def test_entity_manage__manageable(self):
        project, permission = _project_and_permission(admin=True)
        entity_source = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        entity_target = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity_source)
        db.session.add(entity_target)
        rel = Relation(source=entity_source, target=entity_target)
        db.session.add(rel)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertTrue(authz.relation_manage(rel))

    def test_entity_manage__unmanageable(self):
        project, permission = _project_and_permission(admin=False)
        entity_source = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        entity_target = \
            Entity(project=project, status=authz.PUBLISHED_THRESHOLD)
        db.session.add(entity_source)
        db.session.add(entity_target)
        rel = Relation(source=entity_source, target=entity_target)
        db.session.add(rel)
        db.session.commit()
        with self.app.test_request_context():
            flask.session['id'] = 1
            self.app.preprocess_request()
            self.assertFalse(authz.relation_manage(rel))


if __name__ == '__main__':
    unittest.main()
