from datetime import datetime
from app import db, breakpoint
from app.users import constants as USER
from group import group_member_list
from werkzeug import generate_password_hash

class User(db.Model):

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    openid = db.Column(db.String(200), unique = True)
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

    def __init__(self, name, email, password = None, openid = None):
        self.name = name
        self.email = email
        self.openid = openid
        self.creation_time = datetime.utcnow()
        if password is not None:
            if password.startswith('sha1$'):
                self.password = password
            else:  # If we somehow got passed in a raw password, hash it
                self.password = generate_password_hash(password)

    def getStatus(self):
        return USER.STATUS[self.status]
        
    def getRole(self):
        return USER.ROLE[self.role]

    def isUserInContactList(self, user):
        count = self.contacts.filter_by(target_user_id = user.id).count()
        return count > 0
        
    def isFavorited(self, photo):
        return photo in [x.photo for x in self.favorites]

    def unread_pm_count(self):
        from private_message import PrivateMessage  # fuck me, really?
        return PrivateMessage.query.filter_by(recipient_id = self.id).filter_by(isRead = False).count()
        
    def __repr__(self):
        return '<User %r>' % (self.name)
