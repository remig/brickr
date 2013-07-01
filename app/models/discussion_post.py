from datetime import datetime
from app import db

class DiscussionPost(db.Model):

    __tablename__ = 'discussion_post'
    id = db.Column(db.Integer, primary_key = True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('discussion_post.id'))
    post = db.Column(db.Text())
    creation_time = db.Column(db.DateTime)

    def __init__(self, discussion, user, post_text, parent_id = None):
        self.discussion_id = discussion.id
        self.user_id = user.id
        self.parent_id = parent_id
        self.post = post_text
        self.creation_time = datetime.utcnow()

    def __repr__(self):
        return '<Post %d>' % (self.id)