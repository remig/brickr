import flask
from nose import *
from nose.tools import *
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class PhotoModelTestCase(BaseTestCase):

    def test_creation(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))
        
        assert_obj_subset({'id': 1, 'user_id': user.id, 'title': 'new_photo.jpg', 
            'description': 'Description text goes here', 'views': 0}, photo)
        eq_(photo.creation_time, util.now())
    
        photo = self.add(Photo('new_photo.jpg', user, 'photo title', 'desc'))
        assert_obj_subset({'id': 2, 'user_id': user.id, 'title': 'photo title', 
            'description': 'desc', 'views': 0}, photo)
        eq_(photo.creation_time, util.now())

    def test_repr(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user, 'photo title', 'desc'))
        eq_(str(photo), "<Photo 1>")
    
    def test_assoc(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))

        eq_(photo.user_id, user.id)
        eq_(photo.user, user)
        eq_(user.photos.count(), 1)
        eq_(user.photos.first(), photo)
        eq_(user.photos.filter_by(id = 1).first(), photo)
        
        photo2 = self.add(Photo('photo2.jpg', user))
        eq_(Photo.query.count(), 2)
        eq_(user.photos.count(), 2)
        eq_(user.photos.get(2), photo2)
        eq_(user.photos.filter_by(id = 2).first(), photo2)

    def test_remove_from_user(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))

        user.photos.remove(photo)
        db.session.commit()
        eq_(Photo.query.count(), 0)
        eq_(user.photos.count(), 0)

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
