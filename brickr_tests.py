import os, unittest, tempfile
import flask
from app import app, db
from app.models import *

_basedir = os.path.abspath(os.path.dirname(__file__))

class BrickrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_filename = os.path.join(_basedir, 'unittest.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.db_filename
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        self.app = app.test_client()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        os.unlink(self.db_filename)

    def login(self, username, password, context = None):
        if context is None:
            context = self.app
        return context.post('users/login/', data = dict(
            email = username,
            password = password
        ), follow_redirects = True)
        
    def logout(self, context = None):
        if context is None:
            context = self.app
        return context.get('users/logout/', follow_redirects = True)
        
    def create_user(self, name, email, password):
        u = User(name, email, password)
        db.session.add(u)
        db.session.commit()
        
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
        assert 'Need stuff here' in rv.data
        
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
        
if __name__ == '__main__':
    unittest.main()
