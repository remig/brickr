from nose import *
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from app import app, db, util, breakpoint
from app.models import *
from test.base import BaseTestCase, assert_obj_subset

class ContactModelTestCase(BaseTestCase):

    def create_contact(self):
        user1 = self.create_user('Remi', 'remi@gmail.com', 'abc')
        user2 = self.create_user('Alyse', 'alyse@gmail.com', 'abc')
        contact = self.add(Contact(user1, user2))
        return user1, user2, contact
    
    def test_creation(self):
        user1 = self.create_user('Remi', 'remi@gmail.com', 'abc')
        user2 = self.create_user('Alyse', 'alyse@gmail.com', 'abc')
        contact = self.add(Contact(user1, user2))
        assert_obj_subset({'id': 1, 'user_id': 1, 'target_user_id': 2}, contact)
        eq_(contact.creation_time, util.now())

    def test_repr(self):
        u1, u2, contact = self.create_contact()
        eq_(str(contact), "<Contact 1, 1 -> 2>")

    def test_assoc(self):
        u1, u2, contact = self.create_contact()

        eq_(contact.user_id, u1.id)
        eq_(contact.user, u1)
        eq_(contact.target_user_id, u2.id)
        eq_(contact.target_user, u2)
        eq_(u1.contacts.count(), 1)
        eq_(u1.contacts.first(), contact)
        eq_(u1.contacts.filter_by(target_user_id = u2.id).first(), contact)
        eq_(u2.contacts.count(), 0)
        
        contact2 = self.add(Contact(u2, u1))
        eq_(Contact.query.count(), 2)
        eq_(u2.contacts.first(), contact2)
        eq_(u2.contacts.count(), 1)
        
    def test_remove(self):
        u1, u2, contact = self.create_contact()

        u1.contacts.remove(contact)
        db.session.commit()
        eq_(Contact.query.count(), 0)
        eq_(u1.contacts.count(), 0)
        
    def test_dupe(self):
        u1, u2, contact = self.create_contact()

        dupe_contact = Contact(u1, u2)
        db.session.add(dupe_contact)
        assert_raises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_to_json(self):
        expected = {
            'id': 1,
            'user': 'Remi',
            'target_user': 'Alyse',
            'creation': str(util.now())
        }
        
        u1, u2, contact = self.create_contact()
        assert_dict_contains_subset(expected, contact.to_json())
