from app import db, util

class Discussion(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    group_id = db.Column(db.Integer, db.ForeignKey('group_tbl.id'))
    title = db.Column(db.String(120), nullable = False)
    creation_time = db.Column(db.DateTime)
    posts = db.relationship('DiscussionPost', backref = 'discussion', lazy = 'dynamic')
    # group created by Group.discussions backref

    def __init__(self, group, title):
        self.group_id = group.id
        self.title = title
        self.creation_time = util.now()
        
    def __repr__(self):
        return '<Discussion %d, %s>' % (self.id or -1, self.title)
        
    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'creation_time': str(self.creation_time)
        }
