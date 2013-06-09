from datetime import datetime
from app import db

class Comment(db.Model):
    
    __tablename = 'comment'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    comment = db.Column(db.Text)
    creation_time = db.Column(db.DateTime)
    parentID = db.Column(db.Integer, db.ForeignKey('comment.id'))
    
    def __init__(self, user, photo, comment):
        self.user_id = user.id
        self.photo_id = photo.id
        self.comment = comment
        self.creation_time = datetime.utcnow()
        
    def __repr__(self):
        return '<Comment %d, user: %d, photo: %d, text: %s>' % (self.id, self.user_id, self.photo_id, self.comment)
