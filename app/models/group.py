from flask import url_for
from sqlalchemy.ext.associationproxy import association_proxy
from app import db, util, breakpoint
from photo import Photo
from user import User

class GroupMemberList(db.Model):
    
    __tablename__  = 'group_member_list'
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key = True)
    group_id = db.Column('group_id', db.Integer, db.ForeignKey('group_tbl.id'), primary_key = True)
    join_time = db.Column('join_time', db.DateTime)
    
    user = db.relationship(User, backref = db.backref("user_groups", cascade = "all, delete-orphan"))
    group = db.relationship("Group", backref = db.backref("user_groups", cascade = "all, delete-orphan"))
    
    def __init__(self, user, group):
        self.user = user
        self.group = group
        self.join_time = util.now()

    def to_json(self):
        groupJSON = self.group.to_json()
        groupJSON['join_time'] = str(self.join_time)
        return groupJSON

class GroupPhotoList(db.Model):
    
    __tablename__  = 'group_photo_list'
    photo_id = db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'), primary_key = True)
    group_id = db.Column('group_id', db.Integer, db.ForeignKey('group_tbl.id'), primary_key = True)
    add_time = db.Column('add_time', db.DateTime)
    
    photo = db.relationship(Photo, backref = db.backref("photo_groups", cascade = "all, delete-orphan"))
    group = db.relationship("Group", backref = db.backref("photo_groups", cascade = "all, delete-orphan"))
    
    def __init__(self, photo, group):
        self.photo = photo
        self.group = group
        self.add_time = util.now()

    def __repr__(self):
        return '<Photo %d - Group %d: %s>' % (self.photo.id, self.group.id, self.add_time)

    def to_json(self):
        groupJSON = self.group.to_json()
        groupJSON['add_time'] = str(self.add_time)
        return groupJSON

class Group(db.Model):

    __tablename__ = 'group_tbl'  # _tbl because 'group' is a reserved word.  bleh
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60), unique = True, nullable = False)
    url_name = db.Column(db.String(60), unique = True, nullable = False)
    description = db.Column(db.Text)
    rules = db.Column(db.Text)
    creation_time = db.Column(db.DateTime)
    discussions = db.relationship('Discussion', backref = 'group', lazy = 'dynamic')
    members = association_proxy('user_groups', 'user')  # TODO: get rid of this, use user_groups always
    # user_groups created by GroupMemberList backref
    # photo_groups created by GroupMemberList backref

    def __init__(self, name, url_name, description = None, rules = None):
        self.name = name
        self.url_name = url_name
        self.description = description
        self.rules = rules
        self.creation_time = util.now()
        
    def getPhotosInAddOrder(self):
        pg = sorted(self.photo_groups, key = lambda x: x.add_time, reverse = True)
        return [p.photo for p in pg]
        
    def getNewestPhoto(self):
        if (self.photo_groups):
            return max(self.photo_groups, key = lambda x: x.add_time).photo
        return None
        
    def __repr__(self):
        return '<Group %d, %s>' % (self.id or -1, self.url_name)

    def to_json(self):
        try:
            url = url_for('groups.group', groupURL = self.url_name)
        except RuntimeError as e:
            url = 'group.html'

        newestPhoto = self.getNewestPhoto()
        last_photo_url = newestPhoto.url() if newestPhoto else ''

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rules': self.rules,
            'creation_time': str(self.creation_time),
            'url': url,
            'photo_count': len(self.photo_groups),
            'last_photo_url': last_photo_url,
            'discussion_count': self.discussions.count()
        }
