from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class DiscussionModelTestCase(BaseTestCase):

    def test_creation(self):
        group = self.add(Group('Test Group', 'test_group'))
        d = self.add(Discussion(group, 'Test Discussion'))
        assert_obj_subset({'id': 1, 'title': 'Test Discussion'}, d)
        eq_(d.creation_time, util.now())

    def test_repr(self):
        group = self.add(Group('Test Group', 'test_group'))
        d = self.add(Discussion(group, 'Test Discussion'))
        eq_(str(d), "<Discussion 1, Test Discussion>")

    def test_group_assoc(self):
        group = self.add(Group('Test Group', 'test_group'))
        d = self.add(Discussion(group, 'Test Discussion'))
        eq_(d.group, group)
        eq_(group.discussions.count(), 1)
        eq_(group.discussions.first(), d)

        d2 = self.add(Discussion(group, 'Test Discussion 2'))
        eq_(group.discussions.count(), 2)
        eq_(group.discussions.get(2), d2)

    def test_to_json(self):
        expected = {
            'id': 1,
            'title': 'Test Discussion',
            'creation_time': str(util.now())
        }
        
        group = self.add(Group('Test Group', 'test_group'))
        d = self.add(Discussion(group, 'Test Discussion'))
        assert_dict_contains_subset(expected, d.to_json())
