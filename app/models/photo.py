from datetime import datetime
from app import db
from tag import tag_list

class Photo(db.Model):

    __tablename = 'photo'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    views = db.Column(db.Integer)
    creation_time = db.Column(db.DateTime)
    binary_url = db.Column(db.String(120))
    comments = db.relationship('Comment', backref = 'photo', lazy = 'dynamic')
    favorites = db.relationship('Favorite', backref = 'photo', lazy = 'dynamic')
    notes = db.relationship('Note', backref = 'photo', lazy = 'dynamic')
    tags = db.relationship('Tag', secondary = tag_list, backref = db.backref('photos', lazy = 'dynamic'))
    
    def __init__(self, filename, user, title, description):
        self.binary_url = filename
        self.user_id = user.id
        self.title = title
        self.description = description
        self.views = 0
        self.creation_time = datetime.utcnow()
        
    def __repr__(self):
        return '<Photo %d>' % (self.id)
        
    # Get the photo previous to this photo from the user's stream, or None if
    # this is the first photo in the stream
    def prevPhoto(self):
        prev = None
        for p in self.user.photos:
            if p == self:
                return prev
            else:
                prev = p
        return None
        
    # Get the photo next to this photo from the user's stream, or None if
    # this is the last photo in the stream
    def nextPhoto(self):
        prev = None
        for p in self.user.photos:
            if prev == self:
                return p
            else:
                prev = p
        return None
        
    # Return a list of the previous two and next two photos adjacent to this
    # photo in this users photo stream.  This will always return exactly 'count'
    # items.  If there aren't enough photos, empty spots will be padded with None
    def getAdjacentPhotoStream(self, count):
        side = count // 2
        pID = self.id
        idList =  range(pID - count, pID) + [pID] + range(pID + 1, pID + 1 + count)
        photoList = self.user.photos
        return [10, 20, 30]
    