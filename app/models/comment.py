from flask import url_for
from app import db, util

class Comment(db.Model):
    
    __tablename = 'comment'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    comment = db.Column(db.Text)
    creation_time = db.Column(db.DateTime)
    parentID = db.Column(db.Integer, db.ForeignKey('comment.id'))
    
    def __init__(self, user, photo, comment, timestamp = None):
        self.user_id = user.id
        self.photo_id = photo.id
        self.comment = comment
        self.creation_time = timestamp or util.now()
        
    def __repr__(self):
        return '<Comment %d, user: %d, photo: %d, text: %s>' % (self.id or -1, self.user_id, self.photo_id, self.comment)

    def to_json(self):
        return {
            'id': self.id,
            'user_name': self.user.name,
            'user_url': url_for('photos.stream', user_url = self.user.url),
            'comment': self.comment,
            'time': str(self.creation_time)
        }
