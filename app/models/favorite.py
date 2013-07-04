from datetime import datetime
from app import db

class Favorite(db.Model):
    
    __tablename = 'comment'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    creation_time = db.Column(db.DateTime)
    
    def __init__(self, user, photo):
        self.user_id = user.id
        self.photo_id = photo.id
        self.creation_time = datetime.utcnow()
        
    def __repr__(self):
        return '<Favorite %d, user: %d, photo: %d>' % (self.id or -1, self.user_id, self.photo_id)
