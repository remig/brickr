from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class TagModelTestCase(BaseTestCase):

    def create_tag(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))
        tag = Tag('Tag Text')
        photo.tags.extend([tag])
        db.session.commit()
        return user, photo, tag
    
    def test_creation(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))
        tag = self.add(Tag('Tag Text'))
        assert_obj_subset({'id': 1, 'description': 'Tag Text', 'url': 'tag_text'}, tag)

    def test_repr(self):
        user, photo, tag = self.create_tag()
        eq_(str(tag), "<Tag 1, Tag Text>")

    def test_assoc(self):
        user, photo, tag = self.create_tag()

        eq_(Tag.query.count(), 1)
        eq_(tag.photos.count(), 1)
        eq_(tag.photos.get(1), photo)
        
        eq_(photo.tags.count(), 1)
        eq_(photo.tags.get(1), tag)
        eq_(photo.tags.filter_by(description = "Tag Text").first(), tag)
        
        tag2 = Tag('Tag2 Text')   # Add second tag to first photo
        photo.tags.extend([tag2])
        db.session.commit()
        eq_(Tag.query.count(), 2)
        eq_(photo.tags.count(), 2)
        eq_(tag2.photos.count(), 1)
        
        photo2 = self.add(Photo('a.jpg', user))  # Add first tag to new photo
        photo2.tags.extend([tag])
        db.session.commit()
        eq_(photo2.tags.count(), 1)
        eq_(tag.photos.count(), 2)

    def test_remove(self):
        user, photo, tag = self.create_tag()

        photo.tags.remove(tag)
        db.session.commit()
        eq_(photo.tags.count(), 0)
        
    def test_get_or_create(self):
        user, photo, tag = self.create_tag()
        eq_(Tag.get_or_create('Tag Text'), tag)
        
        eq_(Tag.query.count(), 1)
        tag2 = Tag.get_or_create('Tag2 Text')
        photo.tags.extend([tag2])
        db.session.commit()
        eq_(Tag.query.count(), 2)

    def test_dupe(self):
        user, photo, tag = self.create_tag()

        dupe = Tag('Tag Text')
        db.session.add(dupe)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_to_json(self):
        expected = {
            'id': 1,
            'desc': 'Tag Text',
            'url': 'tag_text'
        }
        
        user, photo, tag = self.create_tag()
        assert_dict_contains_subset(expected, tag.to_json())
        eq_(photo.to_json()['tags'], [tag.to_json()])
