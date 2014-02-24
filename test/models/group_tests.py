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
        
    # TODO: test photos in groups
        
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

    def test_group_assoc_to_json(self):
        expected = {
            'id': 1,
            'name': 'Test Group',
            'description': 'description text',
            'rules': 'rules text',
            'creation_time': str(util.now()),
            'join_time': str(util.now())
        }
        
        user = self.create_user()
        group = self.add(Group('Test Group', 'test_group', 'description text', 'rules text'))
        group_assoc = GroupMemberList(user, group)
        db.session.commit()
        assert_dict_contains_subset(expected, group_assoc.to_json())
        eq_(user.to_json()['groups'], [group_assoc.to_json()])
