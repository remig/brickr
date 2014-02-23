from flask import url_for
from sqlalchemy.ext.associationproxy import association_proxy
from app import db, util, breakpoint
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

group_photo_list = db.Table('group_photo_list',
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group_tbl.id'))
)

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
    # photos created by Photo.groups backref

    def __init__(self, name, url_name, description = None, rules = None):
        self.name = name
        self.url_name = url_name
        self.description = description
        self.rules = rules
        self.creation_time = util.now()
        
    def __repr__(self):
        return '<Group %d, %s>' % (self.id or -1, self.url_name)

    def to_json(self):
        try:
            url = url_for('groups.group', groupURL = self.url_name)
        except RuntimeError as e:
            url = 'group.html'
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rules': self.rules,
            'creation_time': str(self.creation_time),
            'url': url
        }
