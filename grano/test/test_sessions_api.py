import unittest
import json

from util import make_test_app, tear_down_test_app
#from util import create_fixture_user, AUTHZ

class SessionsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        #create_fixture_user(self.app)

    def tearDown(self):
        tear_down_test_app()

    def test_sessions_get(self):
        res = self.app.get('/api/1/sessions')
        assert res.status_code == 200, 'OK'
        data = json.loads(res.data)
        assert data.get('logged_in') is False, 'Not logged in'
        

if __name__ == '__main__':
    unittest.main()

