import flask
from nose import *
from nose.tools import *
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class CommentModelTestCase(BaseTestCase):

    def create_comment(self):
        user = self.create_user('Remi')
        photo = self.add(Photo('new_photo.jpg', user))
        comment = self.add(Comment(user, photo, 'Comment Text'))
        return user, photo, comment

    def test_create(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))
        comment = self.add(Comment(user, photo, 'Comment Text'))
        assert_obj_subset({'id': 1, 'user_id': 1, 'photo_id': 1, 'comment': 'Comment Text'}, comment)
        eq_(comment.creation_time, util.now())
    
        comment = self.add(Comment(user, photo, 'Second Text'))
        assert_obj_subset({'id': 2, 'user_id': 1, 'photo_id': 1, 'comment': 'Second Text'}, comment)

        user2 = self.create_user('Alyse', 'a@gmail.com')
        comment = self.add(Comment(user2, photo, 'Third Text'))
        assert_obj_subset({'id': 3, 'user_id': 2, 'photo_id': 1, 'comment': 'Third Text'}, comment)

    def test_assoc(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))
        eq_(user.comments.count(), 0)
        eq_(photo.comments.count(), 0)

        c1 = self.add(Comment(user, photo, 'C1 from U1 on P1'))
        eq_(c1.user_id, 1)
        eq_(c1.user, user)
        eq_(c1.photo_id, 1)
        eq_(c1.photo, photo)
        eq_(user.comments.count(), 1)
        eq_(user.comments.first(), c1)
        eq_(photo.comments.count(), 1)
        eq_(photo.comments.first(), c1)

        c2 = self.add(Comment(user, photo, 'C2 from U1 on P1'))
        eq_(c2.user, user)
        eq_(c2.photo, photo)
        eq_(user.comments.count(), 2)
        eq_(user.comments.get(2), c2)
        eq_(photo.comments.count(), 2)
        eq_(photo.comments.get(2), c2)
        
    def test_remove_from_user(self):
        user, photo, comment = self.create_comment()
    
        user.comments.remove(comment)
        db.session.commit()
        eq_(Comment.query.count(), 0)
        eq_(user.comments.count(), 0)
        eq_(photo.comments.count(), 0)

    def test_remove_from_photo(self):
        user, photo, comment = self.create_comment()
    
        photo.comments.remove(comment)
        db.session.commit()
        eq_(Comment.query.count(), 0)
        eq_(user.comments.count(), 0)
        eq_(photo.comments.count(), 0)

    def test_repr(self):
        user, photo, comment = self.create_comment()
        eq_(str(comment), "<Comment 1, user: 1, photo: 1, text: Comment Text>")

    def test_to_json(self):
        expected = {
            'id': 1,
            'user_name': 'Remi',
            'comment': 'Comment Text',
            'time': str(util.now())
        }
        
        user, photo, comment = self.create_comment()
        assert_dict_contains_subset(expected, comment.to_json())
        eq_(photo.to_json()['comments'], [comment.to_json()])
