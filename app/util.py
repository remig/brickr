import os, re, datetime, mimetypes, shutil
import bleach, boto

from StringIO import StringIO
from PIL import Image
from werkzeug import FileStorage
from app import app

bleach.ALLOWED_TAGS.extend([u'img', u'p', u'br'])
bleach.ALLOWED_ATTRIBUTES[u'img'] = [u'src', u'title']

mimetypes.init([])  # Don't use platform's mimetype mapping, which is broken on Windows (http://bugs.python.org/issue10551)

def str_to_url(s):
    url = '_'.join(s.strip().lower().split())  # lower case and replace space with underscore
    url = re.sub('[^a-z0-9_]+', '', url)  # remove anything except letters, numbers and underscore
    return url

def now():
    return datetime.datetime.utcnow()
    
def roundFloat(f):  # In python < 3.0, round() still returns a float
    return int(round(float(f)))

def sanitizeHTML(s):
    return bleach.clean(s, strip=True)
    
# source_file is an instance of werkzeug.FileStorage
# filename is the '/' delimited path to the target bucket, eg: 'img/a/b/c/foo.jpg'
# bucket is an instance of boto.s3.bucket.  If not specified, bucket will be looked up
# returns the created key and bucket
def save_to_s3(source_file, filename, bucket = None):
    content_type = mimetypes.guess_type(filename)
    if (bucket is None):
        conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
        bucket = conn.get_bucket(app.config["S3_BUCKET"])
    key_name = '/'.join([app.config["S3_UPLOAD_DIRECTORY"], filename])
    k = bucket.new_key(key_name)
    k.set_contents_from_file(source_file, headers = {'Content-Type': content_type})
    k.set_acl('public-read')
    return (key_name, bucket)
    
# source_file is an instance of werkzeug.FileStorage
# filename is the os delimited path to the target bucket, eg: 'img/a/b/c/foo.jpg'
def save_locally(source_file, filename):
    full_filename = os.path.join(app.config['BINARY_PATH'], filename)
    path = os.path.split(full_filename)[0]
    if not os.path.exists(path):
        os.makedirs(path)
    fh = file(full_filename, 'wb')
    shutil.copyfileobj(source_file, fh)
    
# Creates a thumbnail of the chosen size and saves it to the chosen file
# Saves to S3 in production, saves locally otherwise
# source_file is an instance of werkzeug.FileStorage or any other file-ish object
def generate_thumb(source_file, filename, size = 75, bucket = None):
    try:
        source_file.seek(0)
        if isinstance(source_file, FileStorage):
            img = Image.open(StringIO(source_file.read()))
        else:
            img = Image.open(source_file)
            
        i_w, i_h = img.size
        if i_w < i_h:
            offset = (i_h - i_w) // 2
            img = img.crop((0, offset, i_w, i_h - offset))  # l, t, r, b
        else:
            offset = (i_w - i_h) // 2
            img = img.crop((offset, 0, i_w - offset, i_h))  # l, t, r, b
        img.thumbnail((size, size), Image.ANTIALIAS)
        
        if app.config['PRODUCTION']:
            img_fh = StringIO()
            img.save(img_fh, 'JPEG')
            img_fh.seek(0)
            save_to_s3(img_fh, filename, bucket)

        else:
            full_filename = os.path.join(app.config['BINARY_PATH'], filename)
            path = os.path.split(full_filename)[0]
            if not os.path.exists(path):
                os.makedirs(path)
            img.save(full_filename, 'JPEG')

        return True
    except:
        return False
