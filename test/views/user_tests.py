import flask
from nose import *
from nose.tools import *
from app import app, db, breakpoint
from app.models import User
from test.base import BaseTestCase

class UserViewTestCase(BaseTestCase):

    def test_root_index(self):
        rv = self.app.get('/')
        assert 'Welcome to brickr' in rv.data
        assert 'This is the home page for brickr' in rv.data
        
    def test_404(self):
        rv = self.app.get('/doom')
        assert 'Page Not Found' in rv.data
        assert 'What you were looking for is just not there.' in rv.data
        
    def test_about(self):
        rv = self.app.get('about')
        assert 'About' in rv.data
        assert 'This is a quick prototype of what brickr will eventually become' in rv.data
        
    def test_login_logout(self):
        self.create_user('Remi', 'remigagne@gmail.com', 'abc')
        rv = self.login('remigagne@gmail.com', 'abc')
        assert 'Successfully logged Remi in!' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('remigagne@gmail.com', 'abcXXX')
        assert 'Wrong email or password' in rv.data
        rv = self.login('remigagne@gmail.comXXX', 'abc')
        assert 'Wrong email or password' in rv.data

#        with app.test_client() as c:
#            rv = self.login('remigagne@gmail.com', 'abc', c)
#            assert 'Successfully logged Remi in!' in rv.data
#            assert flask.session['user_id'] == 1
