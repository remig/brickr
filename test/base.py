import os, unittest
from app import app, db
from app.models import User

class BaseTestCase(unittest.TestCase):

    def setUp(self):
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
        
    def create_user(self, name, email, password):
        u = User(name, email, password = password)
        db.session.add(u)
        db.session.commit()
        return u
