import os
import flask
from sqlalchemy import func
from werkzeug import secure_filename

from app import app, db, breakpoint
from app.models import *

from app.users.decorators import requires_login

mod = flask.Blueprint('photos', __name__, url_prefix = '/photos')

@mod.before_request
def before_request():
    flask.g.user = None
    if 'user_id' in flask.session:
        flask.g.user = User.query.get(flask.session['user_id'])

@mod.route('/')
def root():
    return flask.render_template('photos/stream.html', user = None, users = User)

@mod.route('/<username>/')
def stream(username):
    user = User.query.filter(func.lower(User.name) == func.lower(username)).first()
    if user is None:
        flask.abort(404)

    photos = user.photos
    return flask.render_template('photos/stream.html', user = user, photos = photos)
    
@mod.route('/<username>/<photoID>/')
def photo(username, photoID):
    user = User.query.filter(func.lower(User.name) == func.lower(username)).first()
    if user is None:
        flask.abort(404)
    photo = Photo.query.get(photoID)
    if photo is None:
        flask.abort(404)

    photo.views += 1
    db.session.commit()

    return flask.render_template('photos/photo.html', photo = photo)

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'png'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@mod.route('/upload/', methods = ['GET', 'POST'])
@requires_login
def upload():
    if flask.request.method == 'POST':
        file = flask.request.files['file']
        if file and allowed_file(file.filename):
            username = flask.g.user.name
            pathname = os.path.join(app.config['BINARY_UPLOAD_PATH'], username)
            
            if not os.path.exists(pathname):
                os.makedirs(pathname)
                
            imagename = secure_filename(file.filename)
            filename = os.path.join(pathname, imagename);
            file.save(filename)
            
            photo = Photo(imagename, flask.g.user, imagename, "Description text goes here")
            
            db.session.add(photo)
            db.session.commit()

            flask.flash(u'Image upload success! - File: %s saved, user: %s' % (filename, flask.g.user.name))
            return flask.redirect(flask.url_for('photos.stream', username = flask.g.user.name))
    return flask.render_template('photos/upload.html')

@mod.route('/addComment/', methods = ['POST'])
@requires_login
def addComment():
    if flask.request.method == 'POST':
        photoID = flask.request.form.get('photoID')
        photo = Photo.query.get(photoID)
        if photo:
            comment = Comment(flask.g.user, photo, flask.request.form.get('comment'))
            db.session.add(comment)
            db.session.commit()
        return flask.redirect(flask.url_for('photos.photo', username = photo.user.name, photoID = photo.id))
    
@mod.route('/addFavorite/', methods = ['POST'])
@requires_login
def addFavorite():
    if flask.request.method == 'POST':
        photoID = flask.request.form.get('photoID')
        photo = Photo.query.get(photoID)
        if photo and Favorite.query.filter_by(user_id = flask.g.user.id, photo_id = photoID).count() < 1:
            favorite = Favorite(flask.g.user, photo)
            db.session.add(favorite)
            db.session.commit()
        return flask.redirect(flask.url_for('photos.photo', username = photo.user.name, photoID = photo.id))

@mod.route('/addTag/', methods = ['POST'])
@requires_login
def addTag():
    if flask.request.method == 'POST':
        photoID = flask.request.form.get('photoID')
        photo = Photo.query.get(photoID)
        tag_text = flask.request.form.get('tag').strip()
        if photo:
            if tag_text not in [x.description for x in photo.tags]:
                tag = Tag(tag_text)
                photo.tags.extend([tag])
                db.session.add(tag)
                db.session.commit()
                flask.flash(u'Tag %s added successfully' % tag_text)
            else:
                flask.flash(u'Tag %s already exists for this photo' % tag_text)
        return flask.redirect(flask.url_for('photos.photo', username = photo.user.name, photoID = photo.id))
