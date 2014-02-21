import flask
from nose import *
from nose.tools import *
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class PhotoModelTestCase(BaseTestCase):

    def test_create_photo(self):
        user = self.create_user()
        photo = Photo('new_photo.jpg', user, 'photo title', 'desc')
        db.session.add(photo)
        db.session.commit()
        
        assert_obj_subset({'id': 1, 'user_id': user.id, 'title': 'photo title', 
            'description': 'desc', 'views': 0}, photo)
        eq_(photo.creation_time, util.now())
    
    def test_to_json(self):
        user = self.create_user('Remi', 'remigagne@gmail.com', 'abc')
        expected = {
            'id': 1,
            'title': 'photo title',
            'description': 'desc',
            'user_url': user.url,
            'views': 0,
            'creation_time': str(util.now()),
            'favorite': False,
            'favorites': [],
            'tags': [],
            'comments': [],
            'groups': []
        }
        
        photo = Photo('new_photo.jpg', user, 'photo title', 'desc')
        db.session.add(photo)
        db.session.commit()
        assert_dict_contains_subset(expected, photo.to_json())
