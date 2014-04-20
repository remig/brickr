import os, boto
from flask import g, url_for
from app import app, db, util, breakpoint
from werkzeug import generate_password_hash
from sqlalchemy import desc
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
    dashboard = db.Column(db.String(5000))  # Stores a JSON blob representing the layout & config for each widget in this user's dashboard.
    photos = db.relationship('Photo', backref = 'user', lazy = 'dynamic', cascade = "all, delete, delete-orphan")
    comments = db.relationship('Comment', backref = 'user', lazy = 'dynamic', cascade = "all, delete, delete-orphan")
    favorites = db.relationship('Favorite', backref = 'user', lazy = 'dynamic', cascade = "all, delete, delete-orphan")
    notes = db.relationship('Note', backref = 'user', lazy = 'dynamic', cascade = "all, delete, delete-orphan")
    contacts = db.relationship('Contact', backref = 'user', lazy = 'dynamic', cascade = "all, delete, delete-orphan")
    groups = association_proxy('user_groups', 'group')  # TODO: get rid of this, use user_groups always
    posts = db.relationship('DiscussionPost', backref = 'user', lazy = 'dynamic', cascade = "all, delete, delete-orphan")
    # user_groups created by GroupMemberList backref

    def __init__(self, name, email, real_name = None, openid = None, password = None):
        self.name = name
        self.email = email
        self.openid = openid
        self.real_name = real_name
        self.url = util.str_to_url(name)
        self.creation_time = util.now()
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

    def get_contacts_photo_list(self, count):
        from photo import Photo  # again with the fucky fuck
        contacts = [x.target_user.id for x in self.contacts.all()]
        photos = db.session.query(Photo) \
            .filter(Photo.user_id.in_(contacts)) \
            .order_by(desc(Photo.creation_time)) \
            .limit(count)
        return photos
        
    @property
    def profile_url(self):
        try:
            return url_for('users.profile', user_url = self.url)
        except RuntimeError as e:
            return 'profile.html'

    @property
    def stream_url(self):
        try:
            return url_for('photos.stream', user_url = self.url)
        except RuntimeError as e:
            return 'photos.html'
        
    @property
    def avatar_url(self):
        c = app.config
        if c['PRODUCTION']:
            # TODO: this will get called a lot.  Find a faster way of falling back to default avatar if none exists.
            s3 = boto.connect_s3(c["S3_KEY"], c["S3_SECRET"])
            bucket = s3.get_bucket(c["S3_BUCKET"])
            k = bucket.get_key("/".join([c["S3_UPLOAD_DIRECTORY"], 'avatars', self.url + '.jpg']))
            if k is None:
                return url_for('static', filename = 'img/avatar.jpg')
            return '/'.join([c['S3_LOCATION'], c['S3_BUCKET'], c['S3_UPLOAD_DIRECTORY'], 'avatars', self.url + '.jpg'])

        path = os.path.join(c['BINARY_PATH'], 'avatars', self.url + '.jpg')
        if os.path.exists(path):
            return '/'.join([c['BINARY_URL_PATH'], 'avatars', self.url + '.jpg'])
        try:
            return url_for('static', filename = 'img/avatar.jpg')
        except RuntimeError as e:
            return '/static/img/avatar.jpg'

    def save_avatar(self, source_file):

        if app.config['PRODUCTION']:
            filename = "/".join(['avatars', self.url + '.jpg'])
        else:
            filename = os.path.join('avatars', self.url + '.jpg')

        return util.generate_thumb(source_file, filename, 100)
        
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
        return '<User %d, %s>' % (self.id or -1, self.name)

    def to_json(self):
        return {
            'id': self.id,
            'is_placeholder': bool(self.placeholder),
            'name': self.name,
            'real_name': self.real_name,
            'email': self.email,
            'joined': str(self.creation_time),
            'url': self.url,
            'profile_url': self.profile_url,
            'stream_url': self.stream_url,
            'avatar_url': self.avatar_url,
            'is_current': g.user and g.user == self,  # TODO: this is wrong: use the existing flask session cookie instead
            'contacts': [x.to_json() for x in self.contacts],
            'favorites': [x.to_json() for x in self.favorites],
            'groups': [x.to_json() for x in self.user_groups]
        }
