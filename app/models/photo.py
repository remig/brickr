import os, boto, mimetypes, shutil
from PIL import Image
from StringIO import StringIO
from uuid import uuid4
from werkzeug import secure_filename, FileStorage

from app import app, db, util, breakpoint
from tag import tag_list
from group import group_photo_list
from app.models.note import Note

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
    comments = db.relationship('Comment', backref = 'photo', lazy = 'dynamic', cascade = "all, delete, delete-orphan")
    favorites = db.relationship('Favorite', backref = 'photo', lazy = 'dynamic', cascade = "all, delete, delete-orphan")
    notes = db.relationship('Note', backref = 'photo', lazy = 'dynamic', cascade = "all, delete, delete-orphan")
    tags = db.relationship('Tag', secondary = tag_list, backref = db.backref('photos', lazy = 'dynamic'))
    groups = db.relationship('Group', secondary = group_photo_list, backref = db.backref('photos', lazy = 'dynamic'))
    # user created by User backref

    def __init__(self, filename, user, title, description):
        filename = secure_filename(filename)
        self.binary_url = uuid4().hex + os.path.splitext(filename)[1]
        self.user_id = user.id
        self.title = title
        self.description = description
        self.views = 0
        self.creation_time = util.now()
        
    def __repr__(self):
        return '<Photo %d>' % (self.id or -1)
        
    def url(self):
        if not hasattr(self, '__url'):
            c = app.config
            if c['PRODUCTION']:
                self.__url = '/'.join([c['S3_LOCATION'], c['S3_BUCKET'], c['S3_UPLOAD_DIRECTORY'], 'img', self.url_path(), self.binary_url])
            else:
                self.__url = '/'.join([c['IMG_PATH'], self.url_path(), self.binary_url])
        return self.__url

    def os_filename(self):
        if not hasattr(self, '__os_filename'):
            c = app.config
            if c['PRODUCTION']:
                self.__os_filename = '/'.join([c['S3_LOCATION'], c['S3_BUCKET'], c['S3_UPLOAD_DIRECTORY'], 'img', self.url_path(), self.binary_url])
            else:
                self.__os_filename = os.path.join(c['BINARY_PATH'], 'img', self.os_path(), self.binary_url)
        return self.__os_filename

    def url_thumb(self, size = 75):
        c = app.config
        folder = 'thumb_%d' % (size)
        if c['PRODUCTION']:
            # If a thumbnail doesn't exist on S3, something went wrong earlier - fix it there, not here.  This will get called *a lot*.
#            conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
#            bucket = conn.get_bucket(app.config["S3_BUCKET"])
#            k = bucket.get_key("/".join([app.config["S3_UPLOAD_DIRECTORY"], folder, self.url_path(), self.binary_url]))
#            if k is None:
#                self.generate_thumb(self.os_filename(), size)
            path = '/'.join([c['S3_LOCATION'], c['S3_BUCKET'], c['S3_UPLOAD_DIRECTORY'], folder, self.url_path(), self.binary_url])
            return path
        else:
            path = os.path.join(app.config['BINARY_PATH'], folder, self.os_path(), self.binary_url)
            if not os.path.exists(path):
                self.generate_thumb(self.os_filename(), size)
            return '/'.join(['/binaries', folder, self.url_path(), self.binary_url])

    def generate_thumb(self, source_file, size = 75, bucket = None):  # for now, all thumbnails are assumed squares of width & height = size
        try:
            source_file.seek(0)
            if isinstance(source_file, FileStorage):
                img = Image.open(StringIO(source_file.read()))
            else:
                img = Image.open(source_file)
                
            folder = 'thumb_%d' % (size)
            i_w, i_h = img.size
            if i_w < i_h:
                offset = (i_h - i_w) // 2
                img = img.crop((0, offset, i_w, i_h - offset))  # l, t, r, b
            else:
                offset = (i_w - i_h) // 2
                img = img.crop((offset, 0, i_w - offset, i_h))  # l, t, r, b
            img.thumbnail((size, size), Image.ANTIALIAS)
            
            if app.config['PRODUCTION']:
                if bucket is None:
                    return False  # gah - really?
                content_type = mimetypes.guess_type(self.binary_url)
                img_fh = StringIO()
                img.save(img_fh, 'JPEG')
                img_fh.seek(0)
                sml = bucket.new_key("/".join([app.config["S3_UPLOAD_DIRECTORY"], folder, self.url_path(), self.binary_url]))
                sml.set_contents_from_file(img_fh, headers = {'Content-Type': content_type})
                sml.set_acl('public-read')
            else:
                path = os.path.join(app.config['BINARY_PATH'], folder, self.os_path())
                if not os.path.exists(path):
                    os.makedirs(path)
                img.save(os.path.join(path, self.binary_url), 'JPEG')
            return True
        except:
            return False
            
    # source_file is an instance of werkzeug.FileStorage
    # return True if save successful, False otherwise
    # Saves to a local path in dev, to S3 in prod
    def save_file(self, source_file):
        try:
            if app.config['PRODUCTION']:  # Upload photo file to AWS S3

                content_type = mimetypes.guess_type(self.binary_url)
                conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
                bucket = conn.get_bucket(app.config["S3_BUCKET"])
                key_name = '/'.join([app.config["S3_UPLOAD_DIRECTORY"], 'img', self.url_path(), self.binary_url])
                k = bucket.new_key(key_name)
                k.set_contents_from_file(source_file, headers = {'Content-Type': content_type})
                k.set_acl('public-read')

                if not self.generate_thumb(source_file, 75, bucket):
                    # So, we saved the photo to S3 just fine, but failed to generate 
                    # a thumbnail. This puts us in an inconsistent state.  Drastic 
                    # measures: delete photo and signal fail on the entire upload process.
                    bucket.delete_key(key_name)
                    return False

            else:  # Running locally - store photo in local folder
                path = os.path.join(app.config['BINARY_PATH'], 'img', self.os_path())
                if not os.path.exists(path):
                    os.makedirs(path)
                fn = os.path.join(path, self.binary_url)
                fh = file(fn, 'wb')
                shutil.copyfileobj(source_file, fh)
                
                return self.generate_thumb(source_file, 75)  # Don't care about leaving stray photos locally - delete them yerself
            return True
        except:  # need to log this, or something
            return False

    # Delete the file associated with this photo, either on the local disk or S3
    def delete_file(self):
        try:
            if app.config['PRODUCTION']:  # Delete photo file from AWS S3
                key_name = '/'.join([app.config["S3_UPLOAD_DIRECTORY"], 'img', self.url_path(), self.binary_url])
                thumb_key_name = '/'.join([app.config["S3_UPLOAD_DIRECTORY"], 'thumb_75', self.url_path(), self.binary_url])  # TODO: need to maintain a list of all thumb sizes, and delete each one here
                conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
                bucket = conn.get_bucket(app.config["S3_BUCKET"])
                bucket.delete_key(key_name)
                bucket.delete_key(thumb_key_name)
            else:
                fn = os.path.join(app.config['BINARY_PATH'], 'img', self.os_path(), self.binary_url)
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
        
    # Return a list of the previous and next few photos adjacent to this photo
    # in this users photo stream.  This will always return exactly 'count' items.
    # If the user doesn't have enough photos, empty spots are padded with None.
    def getAdjacentPhotoStream(self, count):
        photoStream = [self]
        for i in range(count // 2):
            photoStream.insert(0, photoStream[0].prevPhoto() if photoStream[0] else None)
            photoStream.append(photoStream[-1].nextPhoto() if photoStream[-1] else None)
        if not count % 2:
            photoStream.pop(0)  # If we need an even number of photos, remove first one
        return photoStream

    # Return a list of this photo's notes sorted largest to smallest by area.
    def getNotesInZOrder(self):
        return sorted(self.notes.all(), key = Note.area, reverse = True)

    def to_json(self, active_user = None):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url(),
            'user': self.user.to_json(),
            'user_url': self.user.url,  # TODO: get rid of this - use user.url instead
            'views': self.views,
            'creation_time': str(self.creation_time),
            'favorite': active_user.isFavorited(self) if active_user else False,
            'favorites': [x.to_json() for x in self.favorites],
            'tags': [x.to_json() for x in self.tags],
            'comments': [x.to_json() for x in self.comments],
            'groups': [x.to_json() for x in self.groups]
        }
