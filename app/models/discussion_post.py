from app import db, util

class DiscussionPost(db.Model):

    __tablename__ = 'discussion_post'
    id = db.Column(db.Integer, primary_key = True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('discussion_post.id'))
    post = db.Column(db.Text())
    creation_time = db.Column(db.DateTime)
    # discussion created by Discussion backref
    # user created by User backref

    def __init__(self, discussion, user, post_text, parent_id = None):
        self.discussion_id = discussion.id
        self.user_id = user.id
        self.parent_id = parent_id
        self.post = post_text
        self.creation_time = util.now()

    def __repr__(self):
        return '<Post %d>' % (self.id or -1)
