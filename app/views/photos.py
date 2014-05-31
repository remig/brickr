from __future__ import division  # Need to use this across the entire project - is there an easy way to do so?

import os, shlex, urllib2, datetime
from StringIO import StringIO
from flask import *
from sqlalchemy import func
from flickrapi import FlickrAPI, FlickrError

from app import app, db, util, breakpoint, strip
from app.models import *

from app.decorators import requires_login

mod = Blueprint('photos', __name__, url_prefix = '/photos')

@mod.route('/')
def root():
    if g.user:
        return render_template('photos/stream.html', user = g.user, photos = g.user.photos)
    return render_template('photos/stream.html', user = None, photos = Photo)

@mod.route('/<user_url>/')
def stream(user_url):
    user = User.query.filter_by(url = user_url).first()
    if user is None:
        return render_template('photos/stream_placeholder_user.html', username = user_url)
    elif user.placeholder:
        return render_template('photos/stream_placeholder_user.html', user = user)

    photos = user.photos
    return render_template('photos/stream.html', user = user, photos = photos)
    
@mod.route('/tags/<tag_url>/')
def tags(tag_url = ''):
    photos = Photo.query.filter(Photo.tags.any(Tag.url.is_(tag_url)))
    return render_template('photos/stream.html', user = None, photos = None, photoList = photos, tag = tag_url)

@mod.route('/<user_url>/tags/<tag_url>/')
def user_tags(user_url = None, tag_url = ''):
    user = User.query.filter_by(url = user_url).first()
    if user is None:
        return render_template('photos/tags.html', username = user_url)
    elif user.placeholder:
        return render_template('photos/stream_placeholder_user.html', user = user)

    photos = Photo.query.filter_by(user_id = user.id).filter(Photo.tags.any(Tag.url.is_(tag_url)))
    return render_template('photos/stream.html', user = user, photos = photos)

@mod.route('/<user_url>/<photoID>/')
def photo(photoID, user_url = None):
    photo = Photo.query.get(photoID)
    if photo is None:
        abort(404)

    photo.views += 1  # TODO: Totally naive view counter - try harder
    db.session.commit()
    
    photoJSON = json.dumps(photo.to_json(g.user))
    return render_template('photos/photo.html', photo = photo, photoJSON = photoJSON)

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
            return redirect(url_for('photos.stream', user_url = g.user.url))
        else:
            flash(u'This type of file cannot be uploaded.')
    return render_template('photos/upload.html')

# TODO: move all JSON only AJAXey routes out of here and into API
@mod.route('/addComment', methods = ['POST'])
@requires_login
def addComment():
    if request.method == 'POST':
        photoID = request.form.get('photoID')
        photo = Photo.query.get(photoID)
        if photo:
            comment_text = util.sanitizeHTML(request.form.get('comment'))
            parentID = request.form.get('parentID')
            comment = Comment(g.user, photo, comment_text, None, parentID)
            db.session.add(comment)
            db.session.commit()
            return jsonify(result = True, comment = json.dumps(comment.to_json()))
    return jsonify(result = False)
    
@mod.route('/removeComment', methods = ['POST'])
@requires_login
def removeComment():
    if request.method == 'POST':
        photoID = request.form.get('photoID')
        photo = Photo.query.get(photoID)
        commentID = request.form.get('commentID')
        comment = Comment.query.get(commentID)
        if photo and comment:
            photo.comments.remove(comment)
            db.session.commit()
            return jsonify(result = True)
    return jsonify(result = False)

@mod.route('/addFavorite', methods = ['POST'])
@requires_login
def addFavorite():
    if request.method == 'POST':
        photoID = request.form.get('photoID')
        photo = Photo.query.get(photoID)
        if photo and Favorite.query.filter_by(user_id = g.user.id, photo_id = photoID).count() < 1:
            favorite = Favorite(g.user, photo)
            db.session.add(favorite)
            db.session.commit()
            return jsonify(result = True, favorite = json.dumps(favorite.to_json()))
    return jsonify(result = False)

@mod.route('/removeFavorite', methods = ['POST'])
@requires_login
def removeFavorite():
    if request.method == 'POST':
        photoID = request.form.get('photoID')
        photo = Photo.query.get(photoID)
        favorite = Favorite.query.filter_by(user_id = g.user.id, photo_id = photoID)
        if photo and favorite.count() > 0:
            favorite = favorite.first()
            db.session.delete(favorite)
            db.session.commit()
            return jsonify(result = True, favorite = json.dumps(favorite.to_json()))
    return jsonify(result = False)

@mod.route('/addTags', methods = ['POST'])
@requires_login
def addTags():
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

        tag_resp = []
        for tag_text in tag_list:
            tag = Tag.get_or_create(tag_text)
            photo.tags.extend([tag])
            tag_resp.append(tag.to_json())
        db.session.commit()
        return jsonify(result = True, tags = tag_resp)
    return jsonify(result = False)

@mod.route('/removeTag', methods = ['POST'])
@requires_login
def removeTag():
    if request.method == 'POST':
        photoID = request.form.get('photoID')
        photo = Photo.query.get(photoID)
        if not photo:
            return jsonify(result = False)

        existing_tags = [x.description.lower() for x in photo.tags]
        tag_text = request.form.get('tag').strip()
        if tag_text.lower() not in existing_tags:
            return jsonify(result = False)
            
        tag = Tag.query.filter_by(description = tag_text).first()
        if tag is None:
            return jsonify(result = False)
        photo.tags.remove(tag)
        db.session.commit()
        if db.session.query('* from tag_list where tag_id = %d' % tag.id).count() < 1:
            db.session.delete(tag)  # TODO: probably not necessary.  Instead, just purge the Tag table occasionally
            db.session.commit()
        return jsonify(result = True)
    return jsonify(result = False)

@mod.route('/_updatePhoto/', methods = ['POST'])
@requires_login
def updatePhoto():
    photoID = request.form.get('photoID')
    photo = Photo.query.get(photoID)
    if not photo:
        return jsonify(result = False)

    photo.title = request.form.get('title')
    photo.description = request.form.get('desc')
    db.session.add(photo)
    db.session.commit()
    return jsonify(result = True)

@mod.route('/_updateNote/', methods = ['POST'])
@requires_login
def updateNote():
    if request.method == 'POST':
        photoID = request.form.get('photoID')
        photo = Photo.query.get(photoID)
        if not photo:
            return jsonify(result = False)

        x = request.form.get('x', type = util.roundFloat)
        y = request.form.get('y', type = util.roundFloat)
        w = request.form.get('w', type = util.roundFloat)
        h = request.form.get('h', type = util.roundFloat)
        
        noteID = request.form.get('noteID', type = int)
        note_text = request.form.get('note_text')
        doDelete = request.form.get('doDelete')

        if noteID > 0:
            note = Note.query.get(noteID)  # note exists - update it
            note.set_coords(x, y, w, h)
            note.comment = note_text
        else:
            note = Note(g.user, photo, note_text, x, y, w, h)

        if doDelete == 'true':
            db.session.delete(note)
        else:
            db.session.add(note)
        db.session.commit()
        return jsonify(result = True, noteID = note.id)
    return jsonify(result = False)

@mod.route('/delete/<photoID>/', methods = ['GET', 'POST'])
@requires_login
def delete(photoID):
    photo = Photo.query.get(photoID)
    if g.user.id != photo.user.id:
        flash(u"You don't have permission to delete this photo.")
        return redirect(url_for('photos.photo', user_url = photo.user.url, photoID = photoID))
    if photo.delete_file():
        db.session.delete(photo)
        db.session.commit()
        flash(u"Photo deleted successfully")
        return redirect(url_for('photos.stream', user_url = g.user.url))
    flash(u'Something went horribly wrong while deleting your photo. It\'s still here...')
    return redirect(url_for('photos.photo', user_url = photo.user.url, photoID = photoID))

@mod.route('/_importFromFlickr/', methods = ['POST'])
@requires_login
def importFromFlickr():

    if g.user is None:
        return jsonify(result = False, error = "You need to be logged in to import from Flickr")
        
    if not g.user.flickr_auth:
        return jsonify(result = False, error = "Your account has not been authenticated with Flickr")

    try:  # Yes yes, a massive try block, the horror! But almost every single line in here throws an error from FlickrAPI
        photoID = request.form.get('photoID')
        api_key = os.environ['PARAM1']
        api_secret = os.environ['PARAM2']
        flickr = FlickrAPI(api_key, api_secret, store_token = False)

        # Get original photo's URL
        sizes = flickr.photos_getSizes(photo_id = photoID).find('sizes')[-1]
        photo_url = sizes.attrib['source']
        img_width = int(sizes.attrib['width'])   # necessary to correctly scale notes
        img_height = int(sizes.attrib['height'])

        # Pull a blob of most of the photo's metadata
        photo_info = flickr.photos_getInfo(photo_id = photoID).find('photo')

        # Check if the person importing this photo actually owns it
        flickr_screen_name = photo_info.find('owner').attrib['username']
        if flickr_screen_name.lower() != g.user.name.lower():
            return jsonify(result = False, error = 'You dog!  You don\'t own this photo!  %s does.  For shame.' % flickr_screen_name)

        # Pull photo's title, desc, timestamps from metadata blob
        flickr_owner_id = photo_info.find('owner').attrib['nsid']  # used to retrieve views
        title = photo_info.find('title').text
        desc = photo_info.find('description').text
        time_taken = photo_info.find('dates').attrib['taken']  # '2013-06-22 11:16:32' ... wtf?
        time_posted = photo_info.find('dates').attrib['posted']  # '1372279163'

        # flickr notes are in a 0..500px coordinate space, where 500 maps to max(img_width, img_height)
        # brickr notes are normalized to a 0..100 % coordinate space, regardless of image aspect ratio (because I'm smarter)
        # flickr notes don't have timestamp info
        scale_w = 500 if img_width >= img_height else (500 / img_height * img_width)
        scale_h = 500 if img_width < img_height else (500 / img_width * img_height)
        notes = []
        for note in photo_info.find('notes'):
            notes.append({
                'user_id': note.attrib['author'],
                'screen_name': note.attrib['authorname'],
                'text': note.text,
                'x': int(note.attrib['x']) / scale_w * 100,
                'y': int(note.attrib['y']) / scale_h * 100,
                'w': int(note.attrib['w']) / scale_w * 100,
                'h': int(note.attrib['h']) / scale_h * 100
            })

        # Photo tags are easy
        tags = []
        for tag in photo_info.find('tags'):
            if tag.attrib['machine_tag'] != '1':  # Ignore ugly automatically created inivisible-to-users tags
                tags.append(tag.attrib['raw'])

        # Import comments - needs its own Flickr API call
        comments = []
        if int(photo_info.find('comments').text) > 0:
            comment_rsp = flickr.photos_comments_getList(photo_id = photoID).find('comments')
            for comment in comment_rsp:
                comments.append({
                    'user_id': comment.attrib.get('author'),
                    'screen_name': comment.attrib.get('authorname'),
                    'timestamp': comment.attrib.get('datecreate'),
                    'iconfarm': comment.attrib.get('iconfarm'),
                    'iconserver': comment.attrib.get('iconserver'),
                    'text': comment.text
                })

        # Import Favorites.  These come in at most 50 per request. Another dedicated Flickr API call
        favorites = []
        favorite_rsp = flickr.photos_getFavorites(photo_id = photoID, per_page = '50').find('photo')
        for fav in favorite_rsp:
            favorites.append({
                'user_id': fav.attrib.get('nsid'),
                'screen_name': fav.attrib.get('username'),
                'timestamp': fav.attrib.get('favedate'),
                'iconfarm': comment.attrib.get('iconfarm'),
                'iconserver': comment.attrib.get('iconserver')
            })

        fav_page_count = int(favorite_rsp.attrib['pages'])
    
        if fav_page_count > 1:
            for i in range(2, fav_page_count + 1):
                favorite_rsp = flickr.photos_getFavorites(photo_id = photoID, page = str(i), per_page = '50').find('photo')
                for fav in favorite_rsp:
                    favorites.append({
                        'user_id': fav.attrib['nsid'],
                        'screen_name': fav.attrib.get('username'),
                        'timestamp': fav.attrib.get('favedate'),
                        'iconfarm': comment.attrib.get('iconfarm'),
                        'iconserver': comment.attrib.get('iconserver')
                    })

        # View count
        # There's no direct flickr API to get a photo's view count (weird)
        # But we can add 'views' to the list of extra info returned by photo.search... (weird)
        # Can't search by photo ID (not weird), but can search by min & max upload time... set those to the photo's upload time, and we find the exact photo... (lucky)
        views = flickr.photos_search(user_id = flickr_owner_id, min_upload_date = time_posted, max_upload_date = time_posted, extras = 'views')
        views = views.find('photos')[0].attrib['views']

    except Exception as e:
        return jsonify(result = False, error = "Fuck me.  Flickr Import went horribly awry.  Send this message to Remi:\n\nPhoto: %s - %s" % (photoID, e.__repr__()))

    try:
        # So, we've pulled absolutely everything about this one photo out of Flickr.
        # Now dump it all into Brickr. You're welcome.
        photo = Photo(photo_url, g.user, title, desc)
        file_object = urllib2.urlopen(photo_url)  # Download photo from Flickr
        fp = StringIO(file_object.read())
        if not photo.save_file(fp):
            return jsonify(result = False, error = "Well shit. So, everything exported FROM Flickr just fine.  But we failed to save the exported photo file.  Send this message to Remi:\n\nPhoto: %s - Flickr Export - %s" % (photoID, photo_url))

            
        # Flickr buddy icon URL:
        # http://farm{icon-farm}.staticflickr.com/{icon-server}/buddyicons/{nsid}.jpg
        # http://farm4.staticflickr.com/3692/buddyicons/72635252@N00.jpg
        photo.views = views
        db.session.add(photo)
        db.session.commit()  # Shit, should do everything in one commit, but we need a photo ID before adding things to the photo...

        for c in comments:
            user = User.get_user_or_placeholder(c['screen_name'], c['user_id'])
            comment = Comment(user, photo, c['text'], datetime.date.fromtimestamp(float(c['timestamp'])))
            db.session.add(comment)

        for n in notes:
            user = User.get_user_or_placeholder(n['screen_name'], n['user_id'])
            note = Note(user, photo, n['text'], n['x'], n['y'], n['w'], n['h'])
            db.session.add(note)

        for t in tags:
            tag = Tag.get_or_create(t)
            photo.tags.extend([tag])
            db.session.add(tag)

        for f in favorites:
            user = User.get_user_or_placeholder(f['screen_name'], f['user_id'])
            fav = Favorite(user, photo)
            db.session.add(fav)

        db.session.commit()

        return jsonify(result = True, url = url_for('photos.photo', user_url = g.user.url, photoID = photo.id))

    except Exception as e:
        return jsonify(result = False, error = "Well shit. So, everything exported FROM flickr just fine.  But dumping it INTO Brickr is apparently too much to ask.  Send this message to Remi:\n\nPhoto: %s - Brickr Import - %s" % (photoID, e.__repr__()))
