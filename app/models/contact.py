from flask import url_for
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
    
    def __init__(self, user, target_user, permission = CONTACT):
        self.user_id = user.id
        self.target_user_id = target_user.id
        self.permission = permission
        self.creation_time = util.now()
        
    def getTargetUser(self):
        return User.query.filter_by(id = self.target_user_id).first()
        
    def __repr__(self):
        return '<Contact %d, %d -> %d>' % (self.id or -1, self.user_id, self.target_user_id)

    def to_json(self):
        target_user = self.getTargetUser()
        return {
            'id': self.id,
            'user': self.user.name,
            'target_user': target_user.name,
            'target_user_url': url_for('photos.stream', user_url = target_user.url),
            'creation': str(self.creation_time)
        }
