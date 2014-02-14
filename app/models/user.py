import re
from datetime import datetime
from app import db, breakpoint
from group import group_member_list
from werkzeug import generate_password_hash

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
    groups = db.relationship('Group', secondary = group_member_list, backref = db.backref('members', lazy = 'dynamic'))
    posts = db.relationship('DiscussionPost', backref = 'user', lazy = 'dynamic')

    def __init__(self, name, email, real_name = None, openid = None, password = None):
        self.name = name
        self.email = email
        self.openid = openid
        self.real_name = real_name
        self.url = User._name_to_url(name)
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
    def _name_to_url(name):
        url = '_'.join(name.strip().lower().split())  # lower case and replace space with underscore
        url = re.sub('[^a-z0-9_]+', '', url)  # remove anything except letters, numbers and underscore

        # urls must be unique. If this url is already taken, append _x to it, where x is the number of urls like this already
        conflict_count = User.query.filter(User.url.like(url + '%')).count()
        if conflict_count > 0:
            url += '_%d' % (conflict_count)
        return url

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
