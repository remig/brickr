from datetime import datetime
from app import db
from user import User

class PrivateMessage(db.Model):
    
    __tablename = 'private_message'
    id = db.Column(db.Integer, primary_key = True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(120))
    text = db.Column(db.Text)
    isRead = db.Column(db.Boolean)
    creation_time = db.Column(db.DateTime)
    parentID = db.Column(db.Integer, db.ForeignKey('private_message.id'))
    
    def __init__(self, sender, recipient, title, text):
        self.sender_id = sender.id
        self.recipient_id = recipient.id
        self.title = title
        self.text = text
        self.isRead = False
        self.creation_time = datetime.utcnow()
       
    @property
    def sender(self):
        return User.query.get(self.sender_id)
        
    @property
    def recipient(self):
        return User.query.get(self.recipient_id)
        
    def __repr__(self):
        return '<PM %d, sender: %d, recipient: %d, title: %s>' % (self.id, self.sender_id, self.recipient_id, self.title)
