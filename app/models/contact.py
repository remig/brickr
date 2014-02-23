from flask import url_for
from sqlalchemy import UniqueConstraint
from app import db, util, breakpoint
from user import User

# Contact permission levels
CONTACT = 0
FRIEND = 1
FAMILY = 2
PERMISSION = {
    CONTACT: 'contact',
    FRIEND: 'friend',
    FAMILY: 'family',
}

class Contact(db.Model):
    
    __tablename = 'contact'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    target_user_id = db.Column(db.Integer)
    permission = db.Column(db.SmallInteger, default = CONTACT)
    creation_time = db.Column(db.DateTime)
    # user created by User backref
    __table_args__ = (UniqueConstraint('user_id', 'target_user_id', name='_user_uc'),)
    
    def __init__(self, user, target_user, permission = CONTACT):
        self.user_id = user.id
        self.target_user_id = target_user.id
        self.permission = permission
        self.creation_time = util.now()
        
    @property
    def target_user(self):
        if not hasattr(self, '__target_user'):
            self.__target_user = User.query.get(self.target_user_id)
        return self.__target_user
        
    def __repr__(self):
        return '<Contact %d, %d -> %d>' % (self.id or -1, self.user_id or -1, self.target_user_id or -1)

    def to_json(self):
        try:
            url = url_for('photos.stream', user_url = self.target_user.url),
        except RuntimeError as e:
            url = 'photos.html'
        return {
            'id': self.id,
            'user': self.user.name,
            'target_user': self.target_user.name,
            'target_user_url': url,
            'creation': str(self.creation_time)
        }
