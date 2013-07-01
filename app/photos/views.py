import os, shlex
from flask import *
from sqlalchemy import func

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

ALLOWED_EXTENSIONS = set(['.jpg', '.jpeg', '.gif', '.png'])
def allowed_file(filename):
    return os.path.splitext(filename)[1] in ALLOWED_EXTENSIONS

@mod.route('/upload/', methods = ['GET', 'POST'])
@requires_login
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            photo = Photo(file.filename, g.user, file.filename, "Description text goes here")
            if photo.save_file(file):
                db.session.add(photo)
                db.session.commit()
                flash(u'Image upload success!')
            else:
                flash(u'Something went horribly wrong while uploading.  Sharks, maybe.')
            return redirect(url_for('photos.stream', username = g.user.name))
        else:
            flash(u'This type of file cannot be uploaded.')
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
            tag = Tag.query.filter_by(description = tag_text).first()
            if tag is None:
                tag = Tag(tag_text)
            photo.tags.extend([tag])
            db.session.add(tag)
        db.session.commit()
        return jsonify(result = True, tags = tag_list)
    return jsonify(result = False)

@mod.route('/_updateNote/', methods = ['POST'])
@requires_login
def updateNote():
    if request.method == 'POST':
        photoID = request.form.get('photoID')
        photo = Photo.query.get(photoID)
        if not photo:
            return jsonify(result = False)

        x = request.form.get('x', type = int)
        y = request.form.get('y', type = int)
        w = request.form.get('w', type = int)
        h = request.form.get('h', type = int)
        
        noteID = request.form.get('noteID', type = int)
        note_text = request.form.get('note_text')
        doDelete = request.form.get('doDelete', type = bool)

        if noteID > 0:
            note = Note.query.get(noteID)  # note exists - update it
            note.set_coords(x, y, w, h)
            note.comment = note_text
        else:
            note = Note(g.user, photo, note_text, x, y, w, h)

        if doDelete:
            db.session.delete(note)
        else:
            db.session.add(note)
        db.session.commit()
        return jsonify(result = True)
    return jsonify(result = False)

@mod.route('/delete/<photoID>/', methods = ['GET', 'POST'])
@requires_login
def delete(photoID):
    photo = Photo.query.get(photoID)
    if g.user.id != photo.user.id:
        flash(u"You don't have permission to delete this photo.")
        return redirect(url_for('photos.photo', username = photo.user.name, photoID = photoID))
    if photo.delete_file():
        db.session.delete(photo)
        db.session.commit()
        return redirect(url_for('photos.stream', username = g.user.name))
    flash(u'Something went horribly wrong while deleting your photo. It\'s still here...')
    return redirect(url_for('photos.photo', username = photo.user.name, photoID = photoID))
