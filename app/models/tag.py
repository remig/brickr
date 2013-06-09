from app import db

tag_list = db.Table('tag_list',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'))
)
    
class Tag(db.Model):

    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(120), unique = True, nullable = False)

    def __init__(self, description = None):
        self.description = description
        
    def __repr__(self):
        return '<Tag %r>' % (self.description)