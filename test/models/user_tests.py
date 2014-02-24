import flask
from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class UserModelTestCase(BaseTestCase):

    def test_creation(self):
        user = self.add(User('Remi', 'remi@gmail.com', password = 'abc'))
        assert_obj_subset({'id': 1, 'name': 'Remi', 'email': 'remi@gmail.com'}, user)
        assert_true(user.password.startswith('sha1$'))
    
        user = self.add(User('Jack', 'jack@gmail.com', 'Jack D', 'http://google.com/openid', 'asdfasdf'))
        assert_obj_subset({'id': 2, 'name': 'Jack', 'email': 'jack@gmail.com', 
            'real_name': 'Jack D', 'openid': 'http://google.com/openid'}, user)
        eq_(user.creation_time, util.now())
        assert_true(user.password.startswith('sha1$'))

    def test_repr(self):
        user = self.add(User('Remi', 'remi@gmail.com', password = 'abc'))
        eq_(str(user), "<User 1, Remi>")
    
    def test_dupe(self):
        user = self.add(User('Remi', 'remi@gmail.com', password = 'abc'))
        
        bad_user = User('Remi', 'test', password = 'abc')
        db.session.add(bad_user)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()
    
        bad_user = User('Jack', 'remi@gmail.com', password = 'abc')
        db.session.add(bad_user)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()

        bad_user = User('Remi***', 'foo', password = 'abc')  # Check if urls conflicts
        db.session.add(bad_user)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_getStatus(self):
        user = self.create_user()
        eq_(user.getStatus(), 'new')

    def test_getRole(self):
        user = self.create_user()
        eq_(user.getRole(), 'user')

    def test_isUserInContactList(self):
        user1 = self.create_user('Remi', 'remi@gmail.com', 'abc')
        user2 = self.create_user('Alyse', 'alyse@gmail.com', 'abc')
        eq_(user1.isUserInContactList(user2), False)
        contact = self.add(Contact(user1, user2))
        eq_(user1.isUserInContactList(user2), True)
 
    def test_isFavorited(self):
        user = self.create_user()
        photo = self.add(Photo('new_photo.jpg', user))
        eq_(user.isFavorited(photo), False)
        fav = self.add(Favorite(user, photo))
        eq_(user.isFavorited(photo), True)

    def test_unread_pn_count(self):
        user1 = self.create_user('Remi', 'remi@gmail.com', 'abc')
        user2 = self.create_user('Alyse', 'alyse@gmail.com', 'abc')
        pm1 = self.add(PrivateMessage(user1, user2, 'Title', 'Body'))
        eq_(user1.unread_pm_count(), 0)
        eq_(user2.unread_pm_count(), 1)
        
        pm2 = self.add(PrivateMessage(user1, user2, 'Title', 'Body'))
        eq_(user2.unread_pm_count(), 2)
        pm2.isRead = True
        db.session.commit()
        eq_(user2.unread_pm_count(), 1)
        pm1.isRead = True
        db.session.commit()
        eq_(user2.unread_pm_count(), 0)

    def test_to_json(self):
        expected = {
            'id': 1,
            'is_placeholder': False,
            'name': 'Remi',
            'real_name': None,
            'email': 'remigagne@gmail.com',
            'joined': str(util.now()),
            'url': 'remi',
            'contacts': [],
            'favorites': [],
            'groups': []
        }
        
        user = self.create_user('Remi', 'remigagne@gmail.com', 'abc')
        assert_dict_contains_subset(expected, user.to_json())
