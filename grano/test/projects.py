import unittest 
from grano.test.util import make_app, teardown_app
from grano.model import Project

class ProjectsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_app()

    def tearDown(self):
        teardown_app(self.app)
        
    def test_user_from_browserid(self):
        project = Project(label='I am a banana!')
        assert 'banana' in project.label, project.to_json()