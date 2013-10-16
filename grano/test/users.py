import unittest 
from grano.test.util import make_app, teardown_app

class UsersTestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_app()

    def tearDown(self):
        teardown_app(self.app)
        
    def test_user_from_browserid(self):
        from grano.model import User
        user = User.from_browserid({'email': 'fake@something.com', 'issuer': 'pudo.org'})
        assert user is not None, user
        assert User.objects.count()==1, User.objects.all()
