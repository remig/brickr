from flask import url_for
from app import db, util

class Comment(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    comment = db.Column(db.Text)
    creation_time = db.Column(db.DateTime)
    parentID = db.Column(db.Integer, db.ForeignKey('comment.id'))
    # user created by User.comments backref
    # photo created by Photo.comments backref
    
    def __init__(self, user, photo, comment, timestamp = None, parentID = None):
        self.user_id = user.id
        self.photo_id = photo.id
        self.comment = comment
        self.creation_time = timestamp or util.now()
        self.parentID = parentID
        
    def __repr__(self):
        return '<Comment %d, user: %d, photo: %d, text: %s>' % (self.id or -1, self.user_id, self.photo_id, self.comment)

    def to_json(self):
        return {
            'id': self.id,
            'user_name': self.user.name,
            'user_url': self.user.stream_url,  # TODO: rename this to stream_url
            'user_avatar_url': self.user.avatar_url,
            'comment': util.sanitizeHTML(self.comment),
            'parentID': self.parentID,
            'time': str(self.creation_time)
        }
