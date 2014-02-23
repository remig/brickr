from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class NoteModelTestCase(BaseTestCase):

    def create_note(self, x = 0, y = 0, w = 0, h = 0):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))
        note = self.add(Note(user, photo, 'Note Text', x, y, w, h))
        return user, photo, note
    
    def test_creation(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))
        note = self.add(Note(user, photo, 'Note Text', 0, 0, 0, 0))
        assert_obj_subset({'id': 1, 'user_id': 1, 'photo_id': 1, 
            'comment': 'Note Text', 'x': 0, 'y': 0, 'w': 0, 'h': 0}, note)
        eq_(note.creation_time, util.now())

    def test_repr(self):
        user, photo, note = self.create_note()
        eq_(str(note), "<Note 1, user: 1, photo: 1, pos: (0, 0, 0, 0)>")

    def test_assoc(self):
        user, photo, note = self.create_note()

        eq_(note.user_id, user.id)
        eq_(note.user, user)
        eq_(note.photo_id, photo.id)
        eq_(note.photo, photo)

        eq_(user.notes.count(), 1)
        eq_(user.notes.first(), note)
        eq_(user.notes.filter_by(photo_id = photo.id).first(), note)
        
        eq_(photo.notes.count(), 1)
        eq_(photo.notes.first(), note)
        eq_(photo.notes.filter_by(user_id = user.id).first(), note)

    def test_remove_from_user(self):
        user, photo, note = self.create_note()

        user.notes.remove(note)
        db.session.commit()
        eq_(Favorite.query.count(), 0)
        eq_(user.notes.count(), 0)
        eq_(photo.notes.count(), 0)
        
    def test_remove_from_photo(self):
        user, photo, note = self.create_note()

        photo.notes.remove(note)
        db.session.commit()
        eq_(Favorite.query.count(), 0)
        eq_(user.notes.count(), 0)
        eq_(photo.notes.count(), 0)
        
    def test_coord_bounds(self):  # note bounds are normalized to (0,100) inclusive
        user, photo, note = self.create_note(-10, 101, 110, -1)
        eq_(note.x, 0)
        eq_(note.y, 100)
        eq_(note.w, 100)
        eq_(note.h, 0)
        
    def test_coords_getter(self):
        user, photo, note = self.create_note(0, 0, 50, 50)
        eq_(note.coords(), "0_0_50_50")
        note2 = self.add(Note(user, photo, '', 10, 20, 50, 60))
        eq_(note2.coords(), "10_20_50_60")

    def test_area_getter(self):
        user, photo, note = self.create_note(0, 0, 50, 50)
        eq_(note.area(), 2500)
        note2 = self.add(Note(user, photo, '', 10, 20, 101, 200))
        eq_(note2.area(), 10000)

    def test_to_json(self):
        expected = {
            'id': 1, 'user_id': 1, 'photo_id': 1,
            'x': 0, 'y': 0, 'w': 0, 'h': 0
        }
        
        user, photo, note = self.create_note()
        assert_dict_contains_subset(expected, note.to_json())
