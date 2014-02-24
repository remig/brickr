from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class PMModelTestCase(BaseTestCase):

    def create_pm(self):
        user1 = self.create_user('Remi', 'remi@gmail.com', 'abc')
        user2 = self.create_user('Alyse', 'alyse@gmail.com', 'abc')
        pm = self.add(PrivateMessage(user1, user2, 'Title', 'Body'))
        return user1, user2, pm
    
    def test_creation(self):
        user1 = self.create_user('Remi', 'remi@gmail.com', 'abc')
        user2 = self.create_user('Alyse', 'alyse@gmail.com', 'abc')
        pm = self.add(PrivateMessage(user1, user2, 'Title', 'Body'))
        assert_obj_subset({'id': 1, 'sender_id': 1, 'recipient_id': 2,
            'title': 'Title', 'text': 'Body', 'isRead': False}, pm)
        eq_(pm.creation_time, util.now())

    def test_repr(self):
        u1, u2, pm = self.create_pm()
        eq_(str(pm), "<PM 1, sender: 1, recipient: 2, title: Title>")

    def test_assoc(self):
        u1, u2, pm = self.create_pm()

        eq_(PrivateMessage.query.count(), 1)
        eq_(pm.sender_id, 1)
        eq_(pm.recipient_id, 2)
        eq_(pm.sender, u1)
        eq_(pm.recipient, u2)
        
    def test_remove(self):
        u1, u2, pm = self.create_pm()

        db.session.delete(pm)
        db.session.commit()
        eq_(PrivateMessage.query.count(), 0)
        
    def test_to_json(self):
        expected = {
            'id': 1, 'sender_id': 1, 'recipient_id': 2,
            'title': 'Title', 'text': 'Body', 'isRead': False,
            'time': str(util.now())
        }
        
        u1, u2, pm = self.create_pm()
        assert_dict_contains_subset(expected, pm.to_json())
