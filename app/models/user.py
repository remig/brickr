from datetime import datetime
from app import db
from app.users import constants as USER
from group import group_member_list

class User(db.Model):

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = True)
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(20))
    role = db.Column(db.SmallInteger, default = USER.USER)
    status = db.Column(db.SmallInteger, default = USER.NEW)
    creation_time = db.Column(db.DateTime)
    photos = db.relationship('Photo', backref = 'user', lazy = 'dynamic')
    comments = db.relationship('Comment', backref = 'user', lazy = 'dynamic')
    favorites = db.relationship('Favorite', backref = 'user', lazy = 'dynamic')
    notes = db.relationship('Note', backref = 'user', lazy = 'dynamic')
    contacts = db.relationship('Contact', backref = 'user', lazy = 'dynamic')
    groups = db.relationship('Group', secondary = group_member_list, backref = db.backref('members', lazy = 'dynamic'))

    def __init__(self, name = None, email = None, password = None):
        self.name = name
        self.email = email
        self.password = password
        self.creation_time = datetime.utcnow()
        
    def getStatus(self):
        return USER.STATUS[self.status]
        
    def getRole(self):
        return USER.ROLE[self.role]

    def isUserInContactList(self, user):
        count = self.contacts.filter_by(target_user_id = user.id).count()
        return count > 0
        
    def isFavorited(self, photo):
        return photo in [x.photo for x in self.favorites]
        
    def __repr__(self):
        return '<User %r>' % (self.name)