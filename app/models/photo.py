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
    