from app import db, util

tag_list = db.Table('tag_list',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'))
)
    
class Tag(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(120), unique = True, nullable = False)
    url = db.Column(db.String(120))
    # photos created by Photo.tags backref

    def __init__(self, description):
        self.description = description
        self.url = util.str_to_url(description)
        
    def __repr__(self):
        return '<Tag %d, %s>' % (self.id or -1, self.description)
        
    # If 'description' is an existing tag, retrieve it; if not, create it
    @staticmethod
    def get_or_create(description):
        tag = Tag.query.filter_by(description = description).first()
        return tag or Tag(description)

    def to_json(self, active_user = None):
        return {
            'id': self.id,
            'desc': self.description,
            'url': self.url
        }
