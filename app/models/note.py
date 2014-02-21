from app import db, util

def bound(v, lMin = 0, lMax = 100):
    return min(max(v, lMin), lMax)

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
        self.set_coords(x, y, w, h)
        self.creation_time = util.now()

    def __repr__(self):
        return '<Note %d, user: %d, photo: %d, pos: (%d, %d, %d, %d)>' % (self.id or -1, self.user_id, self.photo_id, self.x, self.y, self.w, self.h)

    def coords(self):
        return '%d_%d_%d_%d' % (self.x, self.y, self.w, self.h)

    def set_coords(self, x, y, w, h):
        self.x = bound(x)
        self.y = bound(y)
        self.w = bound(w)
        self.h = bound(h)

    def area(self):
        return self.w * self.h
