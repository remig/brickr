from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class FavoriteModelTestCase(BaseTestCase):

    def create_favorite(self):
        user = self.create_user('Remi')
        photo = self.add(Photo('new_photo.jpg', user))
        fav = self.add(Favorite(user, photo))
        return user, photo, fav
    
    def test_creation(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))
        fav = self.add(Favorite(user, photo))
        assert_obj_subset({'id': 1, 'user_id': 1, 'photo_id': 1}, fav)
        eq_(fav.creation_time, util.now())

    def test_repr(self):
        user, photo, fav = self.create_favorite()
        eq_(str(fav), "<Favorite 1, user: 1, photo: 1>")

    def test_assoc(self):
        user, photo, fav = self.create_favorite()

        eq_(fav.user_id, user.id)
        eq_(fav.user, user)
        eq_(fav.photo_id, photo.id)
        eq_(fav.photo, photo)

        eq_(user.favorites.count(), 1)
        eq_(user.favorites.first(), fav)
        eq_(user.favorites.filter_by(photo_id = photo.id).first(), fav)
        
        eq_(photo.favorites.count(), 1)
        eq_(photo.favorites.first(), fav)
        eq_(photo.favorites.filter_by(user_id = user.id).first(), fav)

    def test_remove_from_user(self):
        user, photo, fav = self.create_favorite()

        user.favorites.remove(fav)
        db.session.commit()
        eq_(Favorite.query.count(), 0)
        eq_(user.favorites.count(), 0)
        eq_(photo.favorites.count(), 0)

    def test_remove_from_photo(self):
        user, photo, fav = self.create_favorite()

        photo.favorites.remove(fav)
        db.session.commit()
        eq_(Favorite.query.count(), 0)
        eq_(user.favorites.count(), 0)
        eq_(photo.favorites.count(), 0)
        
    def test_dupe(self):
        user, photo, fav = self.create_favorite()

        dupe = Favorite(user, photo)
        db.session.add(dupe)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_to_json(self):
        expected = {
            'id': 1,
            'user_name': 'Remi'
        }
        
        user, photo, fav = self.create_favorite()
        fav_json = fav.to_json()
        assert_dict_contains_subset(expected, fav_json)
        eq_(user.to_json()['favorites'], [fav_json])
        eq_(photo.to_json()['favorites'], [fav_json])
