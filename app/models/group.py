from datetime import datetime
from app import db

group_member_list = db.Table('group_member_list',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group_tbl.id'))
)

group_photo_list = db.Table('group_photo_list',
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group_tbl.id'))
)

class Group(db.Model):

    __tablename__ = 'group_tbl'  # _tbl because 'group' is a reserved word.  bleh
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60), unique = True, nullable = False)
    url_name = db.Column(db.String(60), unique = True, nullable = False)
    description = db.Column(db.Text)
    rules = db.Column(db.Text)
    creation_time = db.Column(db.DateTime)
    discussions = db.relationship('Discussion', backref = 'group', lazy = 'dynamic')

    def __init__(self, name, url_name, description = None, rules = None):
        self.name = name
        self.url_name = url_name
        self.description = description
        self.rules = rules
        self.creation_time = datetime.utcnow()
        
    def __repr__(self):
        return '<Group %d - %s>' % (self.id or -1, self.url_name)
