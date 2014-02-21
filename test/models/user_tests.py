import flask
from nose import *
from nose.tools import *
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class UserModelTestCase(BaseTestCase):

    def test_create_user(self):
        user = User('Remi', 'remi@gmail.com', password = 'abc')
        db.session.add(user)
        db.session.commit()
        assert_obj_subset({'id': 1, 'name': 'Remi', 'email': 'remi@gmail.com'}, user)
        assert_true(user.password.startswith('sha1$'))
    
        user = User('Jack', 'jack@gmail.com', 'Jack D', 'http://google.com/openid', 'asdfasdf')
        db.session.add(user)
        db.session.commit()
        assert_obj_subset({'id': 2, 'name': 'Jack', 'email': 'jack@gmail.com', 
            'real_name': 'Jack D', 'openid': 'http://google.com/openid'}, user)
        eq_(user.creation_time, util.now())
        assert_true(user.password.startswith('sha1$'))

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
