import os, boto, mimetypes
from uuid import uuid4
from datetime import datetime
from app import app, db, breakpoint
from tag import tag_list
from group import group_photo_list
from werkzeug import secure_filename

mimetypes.init([])  # Don't use platform's mimetype mapping, which is broken on Windows (http://bugs.python.org/issue10551)

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
    groups = db.relationship('Group', secondary = group_photo_list, backref = db.backref('photos', lazy = 'dynamic'))

    def __init__(self, filename, user, title, description):
        filename = secure_filename(filename)
        self.binary_url =  uuid4().hex + os.path.splitext(filename)[1]
        self.user_id = user.id
        self.title = title
        self.description = description
        self.views = 0
        self.creation_time = datetime.utcnow()
        
    def __repr__(self):
        return '<Photo %d>' % (self.id)
        
    def filename(self):
        if len(self.binary_url) > 5:
            return '/'.join(['img', self.url_path(), self.binary_url])  # yuck
        return str(self.id) + self.binary_url

    # source_file is an instance of FileStorage, with 'save' and 'readlines' properties
    # return true if save successful, false otherwise
    # Saves to a local path in dev, to S3 in prod
    def save_file(self, source_file):
        try:
            if 0 and app.config['PRODUCTION']:  # Upload photo file to AWS S3 - NYI for now

                content_type = mimetypes.guess_type(self.binary_url)
                conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
                bucket = conn.get_bucket(app.config["S3_BUCKET"])
                sml = bucket.new_key("/".join([app.config["S3_UPLOAD_DIRECTORY"], self.url_path(), self.binary_url]))
                sml.set_contents_from_file(source_file, headers = {'Content-Type': content_type})
                sml.set_acl('public-read')

            else:  # Running locally - store photo in local folder
                path = os.path.join(app.config['BINARY_PATH'], self.os_path())
                if not os.path.exists(path):
                    os.makedirs(path)
                fn = os.path.join(path, self.binary_url)
                source_file.save(fn)
            return True
        except:  # need to log this, or something
            return False
            
    # Delete the file associated with this photo, either on the local disk or S3
    def delete_file(self):
        try:
            if 0 and app.config['PRODUCTION']:  # Delete photo file from AWS S3 - NYI for now
                pass
            else:
                if len(self.binary_url) > 5:
                    fn = os.path.join(app.config['BINARY_PATH'], self.os_path(), self.binary_url)
                else:
                    fn = os.path.join(app.config['BINARY_UPLOAD_PATH'], str(self.id) + self.binary_url)
                os.unlink(fn)
            return True
        except:  # need to log this too, damn it
            return False
        
    def url_path(self):
        u = self.binary_url
        return '/'.join([u[0], u[1], u[2]])
        
    def os_path(self):
        u = self.binary_url
        return os.path.join(u[0], u[1], u[2])
    
    # Get the photo previous to this photo from the user's stream, or None if
    # this is the first photo in the stream
    def prevPhoto(self):
        prev = None
        for p in self.user.photos:
            if p == self:
                return prev
            else:
                prev = p
        return None
        
    # Get the photo next to this photo from the user's stream, or None if
    # this is the last photo in the stream
    def nextPhoto(self):
        prev = None
        for p in self.user.photos:
            if prev == self:
                return p
            else:
                prev = p
        return None
        
    # Return a list of the previous two and next two photos adjacent to this
    # photo in this users photo stream.  This will always return exactly 'count'
    # items.  If there aren't enough photos, empty spots are padded with None
    def getAdjacentPhotoStream(self, count):
        photoStream = [self]
        for i in range(count // 2):
            photoStream.insert(0, photoStream[0].prevPhoto() if photoStream[0] else None)
            photoStream.append(photoStream[-1].nextPhoto() if photoStream[-1] else None)
        if not count % 2:
            photoStream.pop(0)  # If we need an even number of photos, remove first one
        return photoStream
    