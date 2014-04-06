from flask import url_for
from sqlalchemy import UniqueConstraint
from app import db, util

class Favorite(db.Model):
    
    __tablename = 'comment'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    creation_time = db.Column(db.DateTime)
    # user created by User.favorites backref
    # photo created by Photo.favorites backref
    __table_args__ = (UniqueConstraint('user_id', 'photo_id', name='_user_uc'),)
    
    def __init__(self, user, photo):
        self.user_id = user.id
        self.photo_id = photo.id
        self.creation_time = util.now()
        
    def __repr__(self):
        return '<Favorite %d, user: %d, photo: %d>' % (self.id or -1, self.user_id, self.photo_id)

    def to_json(self):
        try:
            photo_url = url_for('photos.photo', user_url = self.photo.user.url, photoID = self.photo.id)
        except RuntimeError as e:
            photo_url = 'photo.html'
        return {
            'id': self.id,
            'photo': {
                'id': self.photo_id,
                'title': self.photo.title,
                'thumb_url': self.photo.url_thumb(75),
                'url': photo_url
            },
            'user_name': self.user.name,
            'user_url': self.user.stream_url
        }
