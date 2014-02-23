import flask
from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class UserModelTestCase(BaseTestCase):

    def test_create_user(self):
        user = self.add(User('Remi', 'remi@gmail.com', password = 'abc'))
        assert_obj_subset({'id': 1, 'name': 'Remi', 'email': 'remi@gmail.com'}, user)
        assert_true(user.password.startswith('sha1$'))
    
        user = self.add(User('Jack', 'jack@gmail.com', 'Jack D', 'http://google.com/openid', 'asdfasdf'))
        assert_obj_subset({'id': 2, 'name': 'Jack', 'email': 'jack@gmail.com', 
            'real_name': 'Jack D', 'openid': 'http://google.com/openid'}, user)
        eq_(user.creation_time, util.now())
        assert_true(user.password.startswith('sha1$'))

    def test_repr(self):
        user = self.add(User('Remi', 'remi@gmail.com', password = 'abc'))
        eq_(str(user), "<User 1, Remi>")
    
    def test_dupe_user(self):
        user = self.add(User('Remi', 'remi@gmail.com', password = 'abc'))
        
        bad_user = User('Remi', 'test', password = 'abc')
        db.session.add(bad_user)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()
    
        bad_user = User('Jack', 'remi@gmail.com', password = 'abc')
        db.session.add(bad_user)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()

        bad_user = User('Remi***', 'foo', password = 'abc')  # Check if urls conflicts
        db.session.add(bad_user)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_to_json(self):
        expected = {
            'id': 1,
            'is_placeholder': False,
            'name': 'Remi',
            'real_name': None,
            'email': 'remigagne@gmail.com',
            'joined': str(util.now()),
            'url': 'remi',
            'contacts': [],
            'favorites': [],
            'groups': []
        }
        
        user = self.create_user('Remi', 'remigagne@gmail.com', 'abc')
        assert_dict_contains_subset(expected, user.to_json())
