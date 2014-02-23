from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class ContactModelTestCase(BaseTestCase):

    def test_creation(self):
        user1 = self.create_user('Remi', 'remi@gmail.com', 'abc')
        user2 = self.create_user('Alyse', 'alyse@gmail.com', 'abc')
        contact = self.add(Contact(user1, user2))
        assert_obj_subset({'id': 1, 'user_id': 1, 'target_user_id': 2}, contact)
        eq_(contact.creation_time, util.now())

    def test_repr(self):
        user1 = self.create_user('Remi', 'remi@gmail.com', 'abc')
        user2 = self.create_user('Alyse', 'alyse@gmail.com', 'abc')
        contact = self.add(Contact(user1, user2))
        eq_(str(contact), "<Contact 1, 1 -> 2>")

    def test_assoc(self):
        user1 = self.create_user('Remi', 'remi@gmail.com', 'abc')
        user2 = self.create_user('Alyse', 'alyse@gmail.com', 'abc')
        contact = self.add(Contact(user1, user2))

        eq_(contact.user, user1)
        eq_(contact.target_user, user2)
        eq_(user1.contacts.count(), 1)
        eq_(user1.contacts.first(), contact)
        eq_(user2.contacts.count(), 0)

        contact = self.add(Contact(user2, user1))
        eq_(user2.contacts.first(), contact)
        eq_(user2.contacts.count(), 1)

    def test_to_json(self):
        expected = {
            'id': 1,
            'user': 'Remi',
            'target_user': 'Alyse',
            'creation': str(util.now())
        }
        
        user1 = self.create_user('Remi', 'remi@gmail.com', 'abc')
        user2 = self.create_user('Alyse', 'alyse@gmail.com', 'abc')
        contact = self.add(Contact(user1, user2))
        assert_dict_contains_subset(expected, contact.to_json())
