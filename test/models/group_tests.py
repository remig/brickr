import datetime
from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class GroupModelTestCase(BaseTestCase):

    def test_creation(self):
        group = self.add(Group('Test Group', 'test_group', 'description text', 'rules text'))
        assert_obj_subset({'id': 1, 'name': 'Test Group', 'url_name': 
            'test_group', 'description': 'description text', 'rules': 'rules text'}, group)
        eq_(group.creation_time, util.now())

    def test_repr(self):
        group = self.add(Group('Test Group', 'test_group'))
        eq_(str(group), "<Group 1, test_group>")

    def test_dupe(self):
        group = self.add(Group('Test Group', 'test_group'))

        bad_group = Group('Test Group', 'unique_url')
        db.session.add(bad_group)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()

        bad_group = Group('Unique Group', 'test_group')
        db.session.add(bad_group)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_user_group_assoc(self):
        user = self.create_user()
        group = self.add(Group('Test Group', 'test_group', 'description text', 'rules text'))

        group_assoc = GroupMemberList(user, group)
        db.session.commit()
        
        eq_(len(group.members), 1)
        eq_(group.members[0], user)
        
        eq_(len(user.groups), 1)
        eq_(user.groups[0], group)
        
        eq_(len(group.user_groups), 1)
        eq_(group.user_groups[0], group_assoc)

        eq_(len(user.user_groups), 1)
        eq_(user.user_groups[0], group_assoc)
        
        eq_(group_assoc.group, group)
        eq_(group_assoc.user, user)
        
        eq_(group_assoc.join_time, util.now())
        
        user_json = user.to_json()
        eq_(len(user_json['groups']), 1)
        eq_(user_json['groups'][0], group_assoc.to_json())

        #user2 = self.create_user()
        
    def test_photo_group_assoc(self):
        photo = self.create_photo();
        group = self.add(Group('Test Group', 'test_group', 'description text', 'rules text'))
        
        eq_(len(group.photo_groups), 0)
        eq_(len(photo.photo_groups), 0)
        
        group_assoc = GroupPhotoList(photo, group)
        db.session.commit()
        
        eq_(len(group.photo_groups), 1)
        eq_(group.photo_groups[0].photo, photo)
        
        eq_(len(photo.photo_groups), 1)
        eq_(photo.photo_groups[0].group, group)
        
        eq_(group_assoc.add_time, util.now())
        
        photo_json = photo.to_json()
        eq_(len(photo_json['groups']), 1)
        eq_(photo_json['groups'][0], group_assoc.to_json())
        
        # Test second assoc
        photo2 = self.create_photo()
        group_assoc2 = GroupPhotoList(photo2, group)
        
        eq_(len(photo.photo_groups), 1)
        eq_(len(photo2.photo_groups), 1)
        eq_(len(group.photo_groups), 2)
        
        # Test group's convenience API
        photo.creation_time = datetime.datetime.now()
        db.session.commit()
        eq_(group.getNewestPhoto(), photo)
        assert_list_equal(group.getPhotosInAddOrder(), [photo, photo2])
        
        # Two ways to delete an assoc:
        db.session.delete(group_assoc)
        db.session.commit()
        eq_(len(photo.photo_groups), 0)
        eq_(len(group.photo_groups), 1)
        
        eq_(group.getNewestPhoto(), photo2)
        assert_list_equal(group.getPhotosInAddOrder(), [photo2])
        
        group.photo_groups.remove(group_assoc2)
        db.session.commit()
        eq_(len(photo2.photo_groups), 0)
        eq_(len(group.photo_groups), 0)
        
        eq_(group.getNewestPhoto(), None)
        assert_list_equal(group.getPhotosInAddOrder(), [])
        
    def test_to_json(self):
        expected = {
            'id': 1,
            'name': 'Test Group',
            'description': 'description text',
            'rules': 'rules text',
            'creation_time': str(util.now())
        }
        
        group = self.add(Group('Test Group', 'test_group', 'description text', 'rules text'))
        assert_dict_contains_subset(expected, group.to_json())

    def test_user_group_assoc_to_json(self):
        expected = {
            'id': 1,
            'name': 'Test Group',
            'description': 'description text',
            'rules': 'rules text',
            'creation_time': str(util.now()),
            'photo_count': 0,
            'last_photo_url': '',
            'discussion_count': 0,
            'join_time': str(util.now())
        }
        
        user = self.create_user()
        group = self.add(Group('Test Group', 'test_group', 'description text', 'rules text'))
        group_assoc = GroupMemberList(user, group)
        db.session.commit()
        assert_dict_contains_subset(expected, group_assoc.to_json())
        eq_(user.to_json()['groups'], [group_assoc.to_json()])

    def test_photo_group_assoc_to_json(self):
        photo = self.create_photo()
        group = self.add(Group('Test Group', 'test_group', 'description text', 'rules text'))
        group_assoc = GroupPhotoList(photo, group)
        db.session.commit()
        
        expected = {
            'id': 1,
            'name': 'Test Group',
            'description': 'description text',
            'rules': 'rules text',
            'creation_time': str(util.now()),
            'photo_count': 1,
            'last_photo_url': photo.url(),
            'discussion_count': 0,
            'add_time': str(util.now())
        }
        
        assert_dict_contains_subset(expected, group_assoc.to_json())
        eq_(photo.to_json()['groups'], [group_assoc.to_json()])
