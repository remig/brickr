from datetime import datetime
from flask import url_for
from app import db, util, breakpoint
from werkzeug import generate_password_hash
from sqlalchemy.ext.associationproxy import association_proxy

# User role
ADMIN = 0
STAFF = 1
USER = 2
ROLE = {
    ADMIN: 'admin',
    STAFF: 'staff',
    USER: 'user',
}

# user status
INACTIVE = 0
NEW = 1
ACTIVE = 2
STATUS = {
    INACTIVE: 'inactive',
    NEW: 'new',
    ACTIVE: 'active',
}

class User(db.Model):

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    openid = db.Column(db.String(200), unique = True)
    name = db.Column(db.String(50), unique = True)  # user name, screen name, same thing
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(20))  # Should not be used in production
    role = db.Column(db.SmallInteger, default = USER)
    status = db.Column(db.SmallInteger, default = NEW)
    creation_time = db.Column(db.DateTime)
    url = db.Column(db.String(50), unique = True)  # A simplified version of name to be used in urls (eg http://x.com/photos/url)
    real_name = db.Column(db.String(120))
    flickr_auth = db.Column(db.Boolean, default = False)  # If true, this account's screen name is a valid, authenticated Flickr screen name
    placeholder = db.Column(db.String(20))  # If set, this account is not a 'real' user, it's a placeholder used when importing non-existant user info from Flickr.  Will contain user's Flickr ID
    photos = db.relationship('Photo', backref = 'user', lazy = 'dynamic')
    comments = db.relationship('Comment', backref = 'user', lazy = 'dynamic')
    favorites = db.relationship('Favorite', backref = 'user', lazy = 'dynamic')
    notes = db.relationship('Note', backref = 'user', lazy = 'dynamic')
    contacts = db.relationship('Contact', backref = 'user', lazy = 'dynamic')
    groups = association_proxy('user_groups', 'group')
    posts = db.relationship('DiscussionPost', backref = 'user', lazy = 'dynamic')

    def __init__(self, name, email, real_name = None, openid = None, password = None):
        self.name = name
        self.email = email
        self.openid = openid
        self.real_name = real_name
        self.url = util.str_to_url(name)
        self.creation_time = datetime.utcnow()
        if password is not None:
            if password.startswith('sha1$'):
                self.password = password
            else:  # If we somehow got passed in a raw password, hash it
                self.password = generate_password_hash(password)

    def getStatus(self):
        return STATUS[self.status]
        
    def getRole(self):
        return ROLE[self.role]

    def isUserInContactList(self, user):
        count = self.contacts.filter_by(target_user_id = user.id).count()
        return count > 0
        
    def isFavorited(self, photo):
        return photo in [x.photo for x in self.favorites]

    def unread_pm_count(self):
        from private_message import PrivateMessage  # fuck me, really?
        return PrivateMessage.query.filter_by(recipient_id = self.id).filter_by(isRead = False).count()

    @staticmethod
    def _create_placeholder(name, flickr_id):
        count = 1 + User.query.filter(User.placeholder).count()
        user = User(name, 'placeholder_%d@brickr.com' % count)
        user.placeholder = flickr_id
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_or_placeholder(name, flickr_id):
        user = User.query.filter_by(name = name).first()
        if user is None:
            user = User._create_placeholder(name, flickr_id)
        return user

    def __repr__(self):
        return '<User %d, %r>' % (self.id or -1, self.name)

    def to_json(self):
        return {
            'id': self.id,
            'is_placeholder': bool(self.placeholder),
            'name': self.name,
            'real_name': self.real_name,
            'email': self.email,
            'joined': str(self.creation_time),
            'url': self.url,
            'profile_url': url_for('users.profile', user_url = self.url),
            'contacts': [x.to_json() for x in self.contacts],
            'favorites': [x.to_json() for x in self.favorites],
            'groups': [x.to_json() for x in self.user_groups]
        }
