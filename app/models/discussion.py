from datetime import datetime
from app import db

class Discussion(db.Model):

    __tablename__ = 'discussion'
    id = db.Column(db.Integer, primary_key = True)
    group_id = db.Column(db.Integer, db.ForeignKey('group_tbl.id'))
    title = db.Column(db.String(120), nullable = False)
    creation_time = db.Column(db.DateTime)
    posts = db.relationship('DiscussionPost', backref = 'discussion', lazy = 'dynamic')

    def __init__(self, group, title):
        self.group_id = group.id
        self.title = title
        self.creation_time = datetime.utcnow()
        
    def __repr__(self):
        return '<Discussion %d - %s>' % (self.id or -1, self.title)
