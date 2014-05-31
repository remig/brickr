import os, unittest, datetime
from nose.tools import *
from app import app, db, util, breakpoint
from app.models import User, Photo

class BaseTestCase(unittest.TestCase):

    user_count = 0
    
    def setUp(self):
    
        def mock_now():
            return datetime.datetime(2014, 1, 2, 3, 4, 5, 200101)
        util.now = mock_now
            
        self.db_filename = os.path.join(app.config['BASEDIR'], 'unittest.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # + self.db_filename
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        #os.unlink(self.db_filename)

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
        
    def create_user(self, name = None, email = None, password = 'abc'):
        name = name or 'Remi_' + str(BaseTestCase.user_count)
        email = email or name + '@abc.com'
        BaseTestCase.user_count += 1
        u = self.add(User(name, email, password = password))
        return u
        
    def create_photo(self, title = 'new_photo.jpg', user = None):
        user = user or self.create_user()
        return self.add(Photo(title, user))
        
    def add(self, t):
        db.session.add(t)
        db.session.commit()
        return t

def assert_obj_subset(expected, actual):
    for key, val in expected.iteritems():
        eq_(actual.__getattribute__(key), val)
