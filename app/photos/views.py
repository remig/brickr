import os, shlex
from flask import *
from sqlalchemy import func
from werkzeug import secure_filename

from app import app, db, breakpoint, strip
from app.models import *

from app.users.decorators import requires_login

mod = Blueprint('photos', __name__, url_prefix = '/photos')

@mod.route('/')
def root():
    return render_template('photos/stream.html', user = None, photos = Photo)

@mod.route('/<username>/')
def stream(username):
    user = User.query.filter(func.lower(User.name) == func.lower(username)).first()
    if user is None:
        abort(404)

    photos = user.photos
    return render_template('photos/stream.html', user = user, photos = photos)
    
@mod.route('/<username>/<photoID>/')
def photo(photoID, username = None):
    photo = Photo.query.get(photoID)
    if photo is None:
        abort(404)

    photo.views += 1
    db.session.commit()

    return render_template('photos/photo.html', photo = photo)

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'png'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@mod.route('/upload/', methods = ['GET', 'POST'])
@requires_login
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            
            photo = Photo(file.filename, g.user, file.filename, "Description text goes here")
            
            db.session.add(photo)
            db.session.commit()

            username = g.user.name
            pathname = app.config['BINARY_UPLOAD_PATH']            
            imagename = secure_filename(photo.filename())
            filename = os.path.join(pathname, imagename);
            file.save(filename)
            flash(u'Image upload success! - File: %s saved, user: %s' % (filename, username))
            return redirect(url_for('photos.stream', username = username))
    return render_template('photos/upload.html')

@mod.route('/addComment/', methods = ['POST'])
@requires_login
def addComment():
    if request.method == 'POST':
        photoID = request.form.get('photoID')
        photo = Photo.query.get(photoID)
        if photo:
            comment = Comment(g.user, photo, request.form.get('comment'))
            db.session.add(comment)
            db.session.commit()
        return redirect(url_for('photos.photo', username = photo.user.name, photoID = photo.id))
    
@mod.route('/_addFavorite/', methods = ['POST'])
@requires_login
def addFavorite():
    if request.method == 'POST':
        photoID = request.form.get('photoID')
        photo = Photo.query.get(photoID)
        if photo and Favorite.query.filter_by(user_id = g.user.id, photo_id = photoID).count() < 1:
            favorite = Favorite(g.user, photo)
            db.session.add(favorite)
            db.session.commit()
        return redirect(url_for('photos.photo', username = photo.user.name, photoID = photo.id))

@mod.route('/_addTag/', methods = ['POST'])
@requires_login
def addTag():
    if request.method == 'POST':
        photoID = request.form.get('photoID')
        photo = Photo.query.get(photoID)
        if not photo:
            return jsonify(result = False)

        existing_tags = [x.description.lower() for x in photo.tags]
        tag_list = shlex.split(request.form.get('tag').strip())
        tag_list = [strip(x) for x in tag_list]
        tag_list = [x for x in tag_list if x.lower() not in existing_tags]
        if not tag_list:
            return jsonify(result = False)
            
        for tag_text in tag_list:
            tag = Tag(tag_text)
            photo.tags.extend([tag])
            db.session.add(tag)
        db.session.commit()
        return jsonify(result = True, tags = tag_list)
    return jsonify(result = False)
