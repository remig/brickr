from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class DiscussionPostModelTestCase(BaseTestCase):

    def create_one_post(self):
        user = self.create_user()
        group = self.add(Group('Test Group', 'test_group'))
        discussion = self.add(Discussion(group, 'Test Discussion'))
        post = self.add(DiscussionPost(discussion, user, 'Post Text'))
        return post
    
    def test_creation(self):
        post = self.create_one_post()
        assert_obj_subset({'id': 1, 'post': 'Post Text'}, post)
        eq_(post.creation_time, util.now())

    def test_repr(self):
        post = self.create_one_post()
        eq_(str(post), "<Post 1>")

    def test_assoc(self):
        user = self.create_user()
        group = self.add(Group('Test Group', 'test_group'))
        discussion = self.add(Discussion(group, 'Test Discussion'))
        post = self.add(DiscussionPost(discussion, user, 'Post Text'))
        eq_(post.user_id, 1)
        eq_(post.user, user)
        eq_(post.discussion_id, 1)
        eq_(post.discussion, discussion)
        
        eq_(user.posts.count(), 1)
        eq_(user.posts.first(), post)
        eq_(discussion.posts.count(), 1)
        eq_(discussion.posts.first(), post)
        
        post2 = self.add(DiscussionPost(discussion, user, 'Post Text 2'))
        eq_(user.posts.count(), 2)
        eq_(user.posts.get(2), post2)
        eq_(discussion.posts.count(), 2)
        eq_(discussion.posts.get(2), post2)

    def test_to_json(self):
        expected = {
            'id': 1,
            'user_id': 1,
            'discussion_id': 1,
            'text': 'Post Text'
        }
        
        user = self.create_user()
        group = self.add(Group('Test Group', 'test_group'))
        discussion = self.add(Discussion(group, 'Test Discussion'))
        post = self.add(DiscussionPost(discussion, user, 'Post Text'))
        assert_dict_contains_subset(expected, post.to_json())
