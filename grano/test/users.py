import unittest
import json
from grano.test.util import make_app, teardown_app
from grano.model import User


class UsersTestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_app()

    def tearDown(self):
        teardown_app(self.app)
        
    def test_user_from_browserid(self):
        user = User.from_browserid({'email': 'fake@something.com', 'issuer': 'pudo.org'})
        assert user is not None, user
        assert User.objects.count()==1, User.objects.all()

    def test_user_session(self):
        user = User.from_browserid({'email': 'fake@something.com', 'issuer': 'pudo.org'})

        data = json.loads(self.app.get('/api/1/sessions').get_data())
        assert not data.get('logged_in'), data

        with self.app.session_transaction() as sess:
            sess['user_id'] = user.email
            sess['_fresh'] = True
        
        data = json.loads(self.app.get('/api/1/sessions').get_data())
        assert data.get('logged_in'), data
        assert data.get('user').get('email')==user.email