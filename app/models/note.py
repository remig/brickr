from datetime import datetime
from app import db

class Note(db.Model):
    
    __tablename = 'note'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    comment = db.Column(db.Text)
    personNoteID = db.Column(db.Integer)
    x = db.Column(db.SmallInteger)  # These are normalized to 0..100, expressed as a % of the underlying image size
    y = db.Column(db.SmallInteger)
    w = db.Column(db.SmallInteger)
    h = db.Column(db.SmallInteger)
    creation_time = db.Column(db.DateTime)
    
    def __init__(self, user, photo, comment, x, y, w, h):
        self.user_id = user.id
        self.photo_id = photo.id
        self.comment = comment
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.creation_time = datetime.utcnow()

    def __repr__(self):
        return '<Note %d, user: %d, photo: %d, pos: (%d, %d, %d, %d)>' % (self.id, self.user_id, self.photo_id, self.x, self.y, self.w, self.h)

    def coords(self):
        return '%d_%d_%d_%d' % (self.x, self.y, self.w, self.h)
        
    def area(self):
        return self.w * self.h
